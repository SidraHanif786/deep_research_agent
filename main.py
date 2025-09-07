from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL= os.getenv("BASE_URL")
MODEL= os.getenv("MODEL")

set_tracing_disabled(disabled=True)

# Running agent
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)

llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client
)

math_agent: Agent = Agent(
    name="MathAgent",
    instructions="You are a helpful math assistant.",
    model=llm_model) # gemini-2.5 as agent brain - chat completions

async def main():

    result: Runner = await Runner.run(math_agent, "Tell me about recursion in programming.")
    print(result.final_output)

asyncio.run(main())