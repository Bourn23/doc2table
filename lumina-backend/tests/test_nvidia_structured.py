# from litellm import supports_response_schema

# print(supports_response_schema(model="nvidia/llama-3.1-nemotron-nano-8b-v1", custom_llm_provider="nvidia_nim"))

from __future__ import annotations

import asyncio
import os
import json
from agents import Agent, Runner, ModelSettings
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel, Field, ValidationError

# 1. Define the Pydantic model
# This class is now the single source of truth.
class MovieReview(BaseModel):
    title: str = Field(..., description="The title of the movie.")
    # We can add validation rules, which Pydantic handles
    rating: float = Field(
        ..., 
        description="The rating of the movie.", 
        ge=0, 
        le=5
    )

async def main(model_name: str, api_key: str):
    
    # 2. Get the JSON schema dictionary *from* the Pydantic model
    pydantic_schema = MovieReview.model_json_schema()

    # 3. Instantiate the LitellmModel
    llm = LitellmModel(
        model=model_name,
        api_key=api_key
    )

    # 4. Create ModelSettings, passing the auto-generated schema
    # The 'extra_body' now contains the schema from MovieReview.model_json_schema()
    settings = ModelSettings(
        extra_body={"nvext": {"guided_json": pydantic_schema}}
    )

    # 5. Create the Agent
    # We can even pass the schema in the instructions for extra guidance
    agent = Agent(
        name="PydanticAgent",
        instructions=(
            "You are a movie critic assistant. You must extract the title and rating "
            "from the user's review. You must respond in a JSON format that "
            f"perfectly matches this schema: {json.dumps(pydantic_schema)}"
        ),
        model=llm,
        model_settings=settings,
        tools=[],
    )

    # 6. Define a prompt that matches the schema's task
    prompt = (
        "Review: Inception is a really well made film. I rate it four stars out of five."
    )

    print(f"--- Running agent with model: {model_name} ---")
    print(f"Prompt: {prompt}\n")
    print(f"--- Schema being sent to NIM ---")
    print(json.dumps(pydantic_schema, indent=2))
    
    # 7. Run the agent
    result = await Runner.run(agent, prompt)

    print("\n--- Agent's Raw Output String ---")
    print(result.final_output)

    # 8. Parse and validate the output using the Pydantic model
    try:
        # This is the key step: validate the LLM's string output
        parsed_review = MovieReview.model_validate_json(result.final_output)
        
        print("\n--- Parsed & Validated Pydantic Object ---")
        print(parsed_review)
        
        # Now you have a true Python object, not just a dict
        print(f"\nAccessing fields directly:")
        print(f"Title: {parsed_review.title}")
        print(f"Rating: {parsed_review.rating}")
        
    except ValidationError as e:
        print(f"\n--- Error: LLM Output did not match Pydantic schema ---")
        print(e)


if __name__ == "__main__":
    # Get the API key from environment variables or user input
    api_key = os.environ.get("NVIDIA_NIM_API_KEY")
    if not api_key:
        api_key = input("Enter your NVIDIA_NIM_API_KEY: ")

    # Set the model name
    # model = "nvidia_nim/nvidia/llama-3.1-nemotron-nano-8b-v1"
    # model = "nvidia_nim/nvidia/llama-3.3-nemotron-super-49b-v1.5"

    asyncio.run(main(model_name=model, api_key=api_key))