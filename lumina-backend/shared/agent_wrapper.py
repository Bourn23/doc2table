from typing import TYPE_CHECKING, Any, Literal, overload
from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.responses import Response
from openai.types.responses.response_prompt_param import ResponsePromptParam
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.agent_output import AgentOutputSchemaBase
from agents.handoffs import Handoff
from agents.tool import Tool
from agents.tracing.span_data import GenerationSpanData
from agents.tracing.spans import Span
from agents.models.interface import ModelTracing

if TYPE_CHECKING:
    from agents.model_settings import ModelSettings


class NVIDIANIMModel(OpenAIChatCompletionsModel):
    """Custom model for NVIDIA NIM that uses nvext.guided_json instead of response_format"""
    
    @overload
    async def _fetch_response(
        self,
        system_instructions: str | None,
        input: str | list[Any],
        model_settings: "ModelSettings",
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        span: Span[GenerationSpanData],
        tracing: ModelTracing,
        stream: Literal[True],
        prompt: ResponsePromptParam | None = None,
    ) -> tuple[Response, AsyncStream[ChatCompletionChunk]]: ...

    @overload
    async def _fetch_response(
        self,
        system_instructions: str | None,
        input: str | list[Any],
        model_settings: "ModelSettings",
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        span: Span[GenerationSpanData],
        tracing: ModelTracing,
        stream: Literal[False],
        prompt: ResponsePromptParam | None = None,
    ) -> ChatCompletion: ...

    async def _fetch_response(
        self,
        system_instructions: str | None,
        input: str | list[Any],
        model_settings: "ModelSettings",
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        span: Span[GenerationSpanData],
        tracing: ModelTracing,
        stream: bool = False,
        prompt: ResponsePromptParam | None = None,
    ) -> ChatCompletion | tuple[Response, AsyncStream[ChatCompletionChunk]]:
        # Convert response_format to nvext.guided_json for NVIDIA NIM
        if output_schema is not None:
            from agents.models.chatcmpl_converter import Converter
            
            # Get the JSON schema that would be used in response_format
            response_format = Converter.convert_response_format(output_schema)
            
            if response_format and response_format.get("type") == "json_schema":
                json_schema = response_format.get("json_schema", {}).get("schema", {})
                
                # Inject guided_json into model_settings.extra_body using nvext structure
                if model_settings.extra_body is None:
                    model_settings.extra_body = {}
                
                # NVIDIA NIM requires the nvext wrapper
                if "nvext" not in model_settings.extra_body:
                    model_settings.extra_body["nvext"] = {}
                
                model_settings.extra_body["nvext"]["guided_json"] = json_schema
                
                # Clear output_schema to prevent response_format from being set
                output_schema = None
        
        # Call parent's _fetch_response with the modified parameters
        return await super()._fetch_response(
            system_instructions=system_instructions,
            input=input,
            model_settings=model_settings,
            tools=tools,
            output_schema=output_schema,
            handoffs=handoffs,
            span=span,
            tracing=tracing,
            stream=stream,
            prompt=prompt,
        )