from __future__ import annotations

import asyncio

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main(model: str, api_key: str):
    print(f"Using model: {model} with API key: {api_key}")
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    # First try to get model/api key from args
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=False)
    parser.add_argument("--api-key", type=str, required=False)
    args = parser.parse_args()

# BASE_URL = "https://integrate.api.nvidia.com/v1"
    API_KEY = "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"
# MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
    # nvidia_nim/nvidia/llama-3.1-nemotron-nano-8b-v1
    model = args.model or "nvidia_nim/nvidia/llama-3.1-nemotron-nano-8b-v1"
    if not model:
        model = input("Enter a model name for Litellm: ")

    api_key = args.api_key or API_KEY
    if not api_key:
        api_key = input("Enter an API key for Litellm: ")

    asyncio.run(main(model, api_key))