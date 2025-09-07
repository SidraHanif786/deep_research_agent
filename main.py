from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL= os.getenv("BASE_URL")
MODEL= os.getenv("MODEL")

set_tracing_disabled(disabled=True)

# Gemini client
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)
# Model
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client
)

# Define tools 
@function_tool
def multiply(a: int, b: int) -> int:
    """Exact multiplication ___ """
    return a * b

@function_tool
def sum(a: int, b: int) -> int:
    """Exact addition ___ """
    return a + b

# Agent
math_agent: Agent = Agent(
    name="MathAgent",
    instructions="You are a helpful math assistant."
                "Always use tools for math questions. Always follow DMAS rule (division, multiplication, addition, subtraction). "
                "Explain answers clearly and briefly for beginners.",
    model=llm_model,
    tools=[multiply, sum]
    )

async def main():

    result: Runner = await Runner.run(math_agent, "what is 19 + 23 * 2?")
    print(result.final_output)

asyncio.run(main())