from openai import OpenAI, AsyncOpenAI
from agents import Agent, function_tool, Runner, OpenAIChatCompletionsModel, ModelProvider, Model, RunConfig


import asyncio
import os

BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "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"
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
# nim_client = OpenAI(
#   base_url = "https://integrate.api.nvidia.com/v1",
#   api_key = "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"
# )

nim_client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name or MODEL_NAME, openai_client=nim_client)

CUSTOM_MODEL_PROVIDER = CustomModelProvider()

@function_tool
def calculate_sum(a: int, b: int) -> int:
    print(f"[debug] calculating sum of {a} and {b}")
    return a + b

@function_tool
def multiply_numbers(x: int, y: int) -> int:
    print(f"[debug] multiplying {x} and {y}")
    return x * y

agent = Agent(
    name="CalculatorAgent",
    instructions="You are a helpful assistant that can perform basic arithmetic operations using the provided tools.",
    tools=[calculate_sum, multiply_numbers],
)

async def main():
    result = await Runner.run(
        agent,
        "What is the sum of 15 and 27, and then multiply the result by 3?",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER)
    )
    print("FINAL OUTPUT:", result.final_output)
    
if __name__ == "__main__":
    asyncio.run(main())
