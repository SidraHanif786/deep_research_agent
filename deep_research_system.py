from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool, RunContextWrapper
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL= os.getenv("BASE_URL")
MODEL= os.getenv("MODEL")
USER_NAME = os.getenv("USER_NAME")
USER_CITY = os.getenv("USER_CITY")
USER_TOPIC= os.getenv("USER_TOPIC")
USER_ID= os.getenv("USER_ID")

os.environ["OPENAI_API_KEY"] = GEMINI_API_KEY
set_tracing_disabled(disabled=True)

# Gemini client
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)
# Model
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client,
)


# Import agents
from research_agents import research_coordinator, fact_checker_agent, source_evaluator_agent
from planning_agent import planning_agent

# Force all agents to use Gemini model
research_coordinator.model = llm_model
fact_checker_agent.model = llm_model
source_evaluator_agent.model = llm_model
planning_agent.model = llm_model   

# Main research coordinator
lead_researcher = Agent(
    name="Lead Research Coordinator",
    instructions=(
        "You are the lead research coordinator. You manage the entire research process:\n"
        "1. First, hand off to the Planning Agent to break down complex questions\n"
        "2. Then hand off to Research Coordinator to gather information\n"
        "3. Use Fact Checker to verify important claims\n"
        "4. Use Source Evaluator to assess source quality\n"
        "Monitor progress and ensure all research tasks are completed properly.\n"
        "If any agent encounters issues, provide helpful guidance or redirect to appropriate specialist."
    ),
    handoffs=[planning_agent, research_coordinator, fact_checker_agent, 
              source_evaluator_agent],
    model=llm_model
)

class DeepResearchSystem:
    def __init__(self):
        self.user_profile = {
            "name": USER_NAME,
            "city": USER_CITY,
            "topic": USER_TOPIC,
            "user_id": USER_ID
        }
        self.search_cache = {}
    
    async def research(self, query: str, stream_callback=None):
        """Main research workflow with streaming support"""
        print(f"👤 User: {self.user_profile['name']}")
        print(f"🔍 Query: {query}")
        
        if stream_callback:
            stream_callback(f"Starting research on: {query}")
        
        # Add user profile to context
        context = {
            "user": self.user_profile,
            "query": query,
        }
        
        try:
            result = await Runner.run(
                lead_researcher, 
                json.dumps(context),
            )
            return result.final_output
            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            print(f"❌ Error: {error_msg}")
            return error_msg

            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            if stream_callback:
                stream_callback(f"❌ Error: {error_msg}")
            return error_msg
    
  
async def main():
    research_system = DeepResearchSystem()
    
    # Run a specific query
    query = "What are pros and cons of electric cars?"
    result = await research_system.research(query)
    
    print("\n" + "="*30)
    print("FINAL RESEARCH RESULT")
    print("="*30)
    print(result)
    

if __name__ == "__main__":
    asyncio.run(main())