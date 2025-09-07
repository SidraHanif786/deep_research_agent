from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool, RunContextWrapper
import asyncio
import os
from dotenv import load_dotenv
from dataclasses import dataclass

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

# User 
@dataclass
class UserInfo1:
    name: str
    uid: int
    location: str = "Pakistan"

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the age of the user.'''
    return f"User {wrapper.context.name} is 30 years old"

@function_tool
async def fetch_user_location(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the location of the user.'''
    return f"User {wrapper.context.name} is from {wrapper.context.location}"

async def main():
    user_info = UserInfo1(name="Muhammad Qasim", uid=123)

    agent = Agent[UserInfo1](
        name="Assistant",
        tools=[fetch_user_age,fetch_user_location],
        model=llm_model
    )

    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user? current location of his/her?",
        context=user_info,
    )

    print(result.final_output)
    # The user John is 47 years old.


asyncio.run(main())