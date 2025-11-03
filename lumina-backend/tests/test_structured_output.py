import asyncio
import os

from openai import AsyncOpenAI
from typing import Any, Dict, Optional
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    OpenAIChatCompletionsModel
)

from pydantic import BaseModel, Field

BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = "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"
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


# class NVIDIANIMModel(OpenAIChatCompletionsModel):
#     """Custom model for NVIDIA NIM that uses guided_json instead of response_format"""
    
#     async def _fetch_response(
#         self,
#         messages: list,
#         tools: Optional[list] = None,
#         tool_choice: Optional[Any] = None,
#         response_format: Optional[Dict[str, Any]] = None,
#         parallel_tool_calls: Optional[bool] = None,
#         stream: bool = False,
#         stream_options: Optional[Dict[str, Any]] = None,
#         **kwargs
#     ):
#         # Convert response_format to guided_json for NIM
#         if response_format and response_format.get("type") == "json_schema":
#             json_schema = response_format.get("json_schema", {}).get("schema", {})
#             kwargs.setdefault("extra_body", {})["guided_json"] = json_schema
#             response_format = None  # Remove response_format to avoid conflict
        
#         return await super()._fetch_response(
#             messages=messages,
#             tools=tools,
#             tool_choice=tool_choice,
#             response_format=response_format,
#             parallel_tool_calls=parallel_tool_calls,
#             stream=stream,
#             stream_options=stream_options,
#             **kwargs
#         )
from agent_wrapper import NVIDIANIMModel

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."

class MovieReview(BaseModel):
    title: str = Field(..., description="The title of the movie.")
    # We can add validation rules, which Pydantic handles
    rating: float = Field(
        ..., 
        description="The rating of the movie.", 
        ge=0, 
        le=5
    )

async def main():
    agent = Agent(
        name="Assistant",
        instructions="What's the weather like today?",
        model=NVIDIANIMModel(model=MODEL_NAME, openai_client=client),
        # tools=[get_weather],
        output_type=MovieReview,
    )

    result = await Runner.run(agent, "Review: Inception is a really well made film. I rate it four stars out of five.")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())