from openai import AsyncOpenAI
from agents import Agent, Runner, ModelProvider, Model, OpenAIChatCompletionsModel, function_tool, RunConfig
# from agents.extensions.models.litellm_model import LitellmModel

# BASE_URL = "http://a11abe82bd8da4ae79f6100bd89fa0f8-483808785.us-east-1.elb.amazonaws.com:8000/v1"
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
API_KEY = "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"

# 1. create client
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# 2. create custom model provider
class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name or MODEL_NAME, openai_client=client)

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."

CUSTOM_MODEL_PROVIDER = CustomModelProvider()

async def main():
    agent = Agent(
        name="Assistant",
        instructions="detailed thinking off",
        
        tools=[get_weather]
    )
    result = await Runner.run(
        agent,
        "What's the weather in Tokyo?",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER)
    )
    # print the raw tool_calls too
    print("RESULT FOR DEBUGGING", result)
    print("FINAL OUTPUT:", result.final_output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())