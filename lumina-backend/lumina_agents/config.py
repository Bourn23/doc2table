"""
Model configuration and initialization for Lumina agents.

This module centralizes all LLM model configuration, API client setup, and model
selection logic. It provides configured model instances and utilities for choosing
between different models based on task requirements.

Key Components:
- Model instances: gemini_model, nvidia_nim_model, etc.
- LitellmModelSelector: Utility class for model selection
- CustomAgentHooks: Shared hooks for agent logging and monitoring
- Configuration constants: MAX_OUTPUT_TOKEN, LLM_CALL_LIMIT, etc.
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

from agents import Agent, set_tracing_disabled, AgentHooks, RunContextWrapper, Tool
from agents.extensions.models.litellm_model import LitellmModel
from openai import AsyncOpenAI
from shared.agent_wrapper import NVIDIANIMModel

# Load environment variables
load_dotenv()

# Configuration constants
MAX_OUTPUT_TOKEN = 4096
MAX_CSV_ROWS = 20  # Maximum number of rows to process per CSV file for initial screening
LLM_CALL_LIMIT = 4

# Semaphore for controlling concurrent LLM calls
llm_call_semaphore = asyncio.Semaphore(LLM_CALL_LIMIT)

# Disable tracing for cleaner output
set_tracing_disabled(True)

# Set Gemini API key in environment (if available)
gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if gemini_api_key:
    os.environ["GEMINI_API_KEY"] = gemini_api_key


# ============================================================================
# Model Instances
# ============================================================================

# Gemini Models
gemini_model = LitellmModel(
    model='gemini/gemini-2.5-flash',
    api_key=os.getenv("GEMINI_API_KEY") or ""
)

gemini_model_lite = LitellmModel(
    model='gemini/gemini-2.5-flash-lite',
    api_key=os.getenv("GEMINI_API_KEY") or ""
)

# NVIDIA NIM Models
BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = os.getenv("NVIDIA_API_KEY")
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
MODEL_NAME_LARGE = "nvidia/llama-3.3-nemotron-super-49b-v1.5"

nim_client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

nvidia_nim_model = NVIDIANIMModel(model=MODEL_NAME, openai_client=nim_client)
nvidia_nim_model_large = NVIDIANIMModel(model=MODEL_NAME_LARGE, openai_client=nim_client)


# ============================================================================
# Model Selector
# ============================================================================

class LitellmModelSelector:
    """
    Utility class for selecting LLM models based on task requirements.
    
    This class provides a centralized way to choose between different model
    configurations. Currently supports Gemini and NVIDIA NIM models.
    
    Example:
        >>> model = LitellmModelSelector.get_model(use_custom=True)
        >>> agent = Agent(name="MyAgent", model=model, ...)
    """
    
    @staticmethod
    def get_model(use_custom: bool = False) -> LitellmModel:
        """
        Get a model instance based on configuration.
        
        Args:
            use_custom: If True, returns the custom/preferred model configuration.
                       If False, returns the default model.
        
        Returns:
            LitellmModel: Configured model instance ready for use with agents.
        """
        if use_custom:
            return gemini_model
        else:
            return gemini_model


# ============================================================================
# Agent Hooks
# ============================================================================

class CustomAgentHooks(AgentHooks):
    """
    Custom hooks for agent lifecycle events.
    
    Provides logging and monitoring capabilities for agent execution. Tracks
    tool calls and provides visibility into agent behavior during execution.
    
    Args:
        display_name: Human-readable name for the agent (used in log messages)
        verbose: If True, prints detailed execution logs. If False, suppresses output.
    
    Example:
        >>> hooks = CustomAgentHooks(display_name="Schema Agent", verbose=True)
        >>> agent = Agent(name="schema_agent", hooks=hooks, ...)
    """
    
    def __init__(self, display_name: str, verbose: bool = True):
        """
        Initialize agent hooks.
        
        Args:
            display_name: Name to display in log messages
            verbose: Whether to print log messages
        """
        self.event_counter = 0
        self.display_name = display_name
        self.verbose = verbose
        
    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """Called when agent execution starts."""
        if self.verbose:
            print(f"[{self.display_name}] Agent started.")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        """Called when a tool execution starts."""
        self.event_counter += 1
        if self.verbose:
            print(f"[{self.display_name}] Tool '{tool}' started. Event count: {self.event_counter}")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        """Called when a tool execution completes."""
        self.event_counter += 1
        if self.verbose:
            print(
                f"### {self.event_counter}: Tool {tool.name} finished. "
                f"result={result}, name={context.tool_name}, "
                f"call_id={context.tool_call_id}, args={context.tool_arguments}."
            )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Constants
    'MAX_OUTPUT_TOKEN',
    'MAX_CSV_ROWS',
    'LLM_CALL_LIMIT',
    'llm_call_semaphore',
    
    # Model instances
    'gemini_model',
    'gemini_model_lite',
    'nvidia_nim_model',
    'nvidia_nim_model_large',
    
    # Utilities
    'LitellmModelSelector',
    'CustomAgentHooks',
]
