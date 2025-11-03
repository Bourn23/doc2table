import json
from typing import Any
from openai import AsyncOpenAI
from agents import Agent, Runner, ModelProvider, Model, OpenAIChatCompletionsModel, function_tool, RunConfig
# from agents.extensions.models.litellm_model import LitellmModel
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function as ToolFunction,
)

BASE_URL = "http://a51ca87ba811c40f4a082fe2be9ddcb0-1052556339.us-east-1.elb.amazonaws.com:8000/v1"
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
API_KEY = "fake_key_for_ollama"

# 1. create client
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

class NIMToolAwareModel(OpenAIChatCompletionsModel):
    async def _fetch_response(  # type: ignore[override]
        self,
        system_instructions,
        input,
        model_settings,
        tools,
        output_schema,
        handoffs,
        span,
        tracing,
        stream: bool = False,
        prompt=None,
    ):
        # 1. call parent to actually hit NIM
        resp = await super()._fetch_response(
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            span,
            tracing,
            stream,
            prompt,
        )

        # 2. we only patch non-streaming
        from openai.types.chat import ChatCompletion
        if not isinstance(resp, ChatCompletion):
            return resp

        if not resp.choices or not resp.choices[0].message:
            return resp

        msg = resp.choices[0].message

        # if the model ALREADY returned tool_calls in the proper format, do nothing
        if getattr(msg, "tool_calls", None):
            return resp

        # 3. try to parse NIM-style JSON from content
        if msg.content:
            try:
                data = json.loads(msg.content)
            except Exception:
                return resp  # not JSON, leave it

            # handle {"name": "...", "parameters": {...}}
            if isinstance(data, dict) and "name" in data:
                tool_name = data["name"]
                params = data.get("parameters", {})

                # 4. build REAL OpenAI tool-call objects
                msg.tool_calls = [
                    ChatCompletionMessageToolCall(
                        id="call_1",
                        type="function",
                        function=ToolFunction(
                            name=tool_name,
                            arguments=json.dumps(params),
                        ),
                    )
                ]
                # clear content so agent doesn’t think it's final text
                msg.content = None

            # (optional) handle list-of-calls format
            elif isinstance(data, list):
                tool_calls_objs = []
                for i, item in enumerate(data):
                    if not isinstance(item, dict) or "name" not in item:
                        continue
                    tool_calls_objs.append(
                        ChatCompletionMessageToolCall(
                            id=f"call_{i+1}",
                            type="function",
                            function=ToolFunction(
                                name=item["name"],
                                arguments=json.dumps(item.get("parameters", {})),
                            ),
                        )
                    )
                if tool_calls_objs:
                    msg.tool_calls = tool_calls_objs
                    msg.content = None

        return resp


class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return NIMToolAwareModel(
            model=model_name or MODEL_NAME,
            openai_client=client,
        )


CUSTOM_MODEL_PROVIDER = CustomModelProvider()


@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main():
    agent = Agent(
        name="Assistant",
        instructions=(
            "detailed thinking off.\n"
            "You are a helpful assistant.\n"
            "You may call tools.\n"
            "After tools finish, respond to the user in plain English, not JSON.\n"
            "Do NOT GET STUCK IN CALLING TOOLS."
        ),
        tools=[get_weather]
    )
    result = await Runner.run(
        agent,
        "What's the weather in Tokyo?",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER)
    )
    # print the raw tool_calls too
    print("FINAL OUTPUT:", result.final_output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())