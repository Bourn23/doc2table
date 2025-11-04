from agents import Agent, set_tracing_disabled, AgentHooks, RunContextWrapper, Tool, Runner, AgentOutputSchema, ModelSettings, Model, ModelProvider, ModelSettings
from agents.model_settings import ModelSettings
from agents.extensions.models.litellm_provider import LitellmProvider
from agents.extensions.models.litellm_model import LitellmModel
from shared.tools import *
from typing import Dict, Iterable, List, Any, Literal
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
# import litellm
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from agents.agent import StopAtTools
import asyncio
import fitz  # PyMuPDF for PDF processing
import csv
import io
from pydantic import BaseModel, ConfigDict
import os
from dotenv import load_dotenv
from shared.api_types import _Field
import random
from shared.utils import run_agent_gracefully

# This line loads the variables from your .env file into the environment
load_dotenv()

MAX_CSV_ROWS = 20 # maximum number of rows to process per CSV file for initial screening
MAX_OUTPUT_TOKEN = 4096

LLM_CALL_LIMIT = 4
llm_call_semaphore = asyncio.Semaphore(LLM_CALL_LIMIT)

os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_GEMINI_API_KEY")
set_tracing_disabled(True)

# EXTRACTION_LLM_MODEL = "qwen3:0.6b"
# custom_client = AsyncOpenAI(base_url="http://localhost:8080/v1", api_key='fake_key_for_ollama')

gemini_model = LitellmModel(model='gemini/gemini-2.5-flash', api_key=os.getenv("GEMINI_API_KEY"))
gemini_model_lite = LitellmModel(model='gemini/gemini-2.5-flash-lite', api_key=os.getenv("GEMINI_API_KEY"))

# nvidia_nim_model = LitellmModel(model='nvidia_nim/nvidia/llama-3.1-nemotron-nano-8b-v1', api_key=os.getenv("NVIDIA_NIM_API_KEY"))

# GRAPH_LLM_MODEL = os.getenv("GRAPH_LLM_MODEL", "nvidia/llama-3.1-nemotron-nano-8b-v1")
# llm = ChatNVIDIA(model=GRAPH_LLM_MODEL)


### Local Model
# EXTRACTION_LLM_MODEL = "qwen3:0.6b"
# custom_client = AsyncOpenAI(base_url="http://localhost:8080/v1", api_key='fake_key_for_ollama')

### # Local Model (MLX Server)
class CustomLitellmModel(LitellmModel):
    def __init__(self):
        super().__init__(model="openai/default_model", api_key="fake_key_for_ollama", base_url="http://localhost:8080/v1")

### Gemini Model
gemini_model = LitellmModel(model='gemini/gemini-2.5-flash', api_key=os.getenv("GEMINI_API_KEY"))
gemini_model_lite = LitellmModel(model='gemini/gemini-2.5-flash-lite', api_key=os.getenv("GEMINI_API_KEY"))


### NVIDIA Model
from agents import set_default_openai_client, set_default_openai_api
BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = os.getenv("NVIDIA_API_KEY")
MODEL_NAME = "nvidia/llama-3.1-nemotron-nano-8b-v1"
MODEL_NAME_LARGE = "nvidia/llama-3.3-nemotron-super-49b-v1.5"

nim_client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

set_default_openai_client(client=nim_client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)

from shared.agent_wrapper import NVIDIANIMModel
nvidia_nim_model = NVIDIANIMModel(model=MODEL_NAME, openai_client=nim_client)
nvidia_nim_model_large = NVIDIANIMModel(model=MODEL_NAME_LARGE, openai_client=nim_client)
# class CustomModelProvider(ModelProvider):
#     def get_model(self, model_name: str | None) -> Model:
#         return OpenAIChatCompletionsModel(model=model_name or MODEL_NAME, openai_client=nim_client)



# CUSTOM_MODEL_PROVIDER = CustomModelProvider()

class CustomLitellmModel(LitellmModel):
    def __init__(self):
        super().__init__(model="openai/default_model", api_key="fake_key_for_ollama", base_url="http://localhost:8080/v1")


# A custom class to choose either extraction LLM model or CustomLitellmModel based on some condition
class LitellmModelSelector:
    @staticmethod
    def get_model(use_custom: bool = False) -> LitellmModel:
        if use_custom:
            ## approach 1: using a custom LitellmModel directly
            # litellm._turn_on_debug()
            # return CustomLitellmModel()
            
            return gemini_model
            # return nvidia_nim_model
            # return CUSTOM_MODEL_PROVIDER
            
            
            # return llm
            
            # return LitellmProvider().get_model(f'ollama_chat/{EXTRACTION_LLM_MODEL}')
            ## approach 2
            # model = OpenAIChatCompletionsModel(model="openai/default_model", openai_client=custom_client)
            # return model
        else:
            # return LitellmProvider().get_model(f'ollama_chat/{EXTRACTION_LLM_MODEL}')
            return gemini_model
            # return CUSTOM_MODEL_PROVIDER
            # return nvidia_nim_model_large
            # return llm
        
# here's how to use the selector
# model = LitellmModelSelector.get_model(use_custom=True)  # to use Custom

# class LitellmModelSelector:
#     @staticmethod
#     def get_model(use_custom: bool = False):
#         if use_custom:
#             return 'gpt-5-mini'
#         else:
#             return 'gpt-4o'
class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name
        
    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        print(f"[{self.display_name}] Agent started.")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(f"[{self.display_name}] Tool '{tool}' started. Event count: {self.event_counter}")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Tool {tool.name} finished. result={result}, name={context.tool_name}, call_id={context.tool_call_id}, args={context.tool_arguments}."  # type: ignore[attr-defined]
        )
# schema generation agent
SCHEMA_AGENT_PROMPT = """detailed thinking off \nYou are a data extraction expert. Your job is to analyze the user's extraction intention 
and recommend a comprehensive schema of fields to extract from documents.

For each field, you should:
1. Identify the field name (use snake_case)
2. Provide a clear description of what to extract
3. Specify the data type (string, number, boolean, list, object)
4. Include units if it's a measurement
5. Give concrete examples
6. Suggest validation rules if applicable

Anticipate related fields that would be useful. If the user wants temperature data, 
recommend not just temperature but also unit, measurement method, conditions, etc.
KEEP YOUR RECOMMENDATIONS TO A FEW IMPORTANT/PRACTICAL FIELDS (less than 5-6 FIELDS) UNLESS ASKED FOR MORE.
"""

schema_agent = Agent(
    name = "Schema Generation Agent",
    instructions = SCHEMA_AGENT_PROMPT,
    output_type = SchemaRecommendation,
    model = LitellmModelSelector.get_model(use_custom=True),
)

class FieldMapping(BaseModel):
    field_name: str = Field(description="Name of the field")
    description: str = Field(description="Description of the field")

class PydanticModelCode(BaseModel):
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: str = Field(description="Complete Pydantic model code")
    
class ExtractionPrompt(BaseModel):
    prompt_text: str = Field(description="Detailed prompt for extraction agent")
    
# Pydantic model generation agent
class ExtractionSchema(BaseModel):
    """Generated extraction schema with Pydantic model"""
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: PydanticModelCode = Field(description="Complete Pydantic model code")
    extraction_prompt: ExtractionPrompt = Field(description="Detailed prompt for extraction agent")
    field_mappings: List[FieldMapping] = Field(description="Mapping of field names to descriptions")
    
class ExtractionSchemaUpdated(BaseModel):
    """Generated extraction schema with Pydantic model"""
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: PydanticModelCode = Field(description="Complete Pydantic model code")
    extraction_prompt: ExtractionPrompt = Field(description="Detailed prompt for extraction agent")
    field_mappings: List[FieldMapping] = Field(description="Mapping of field names to descriptions")

PYDANTIC_AGENT_PROMPT = """detailed thinking on \n
You are a meticulous Pydantic model architect. Your sole purpose is to convert a user's list of field recommendations into a production-ready Pydantic model.

**INPUT FORMAT:**
You will receive a list of field recommendations as a JSON object. Each field will have a name, a type, and a description.

**YOUR TASK:**
1.  **Create the Model**: Generate a single, complete Pydantic V2 model class.
2.  **Import Necessary Types**: Add all required imports from `pydantic`, `typing`, and `datetime`.
3.  **Add Type Hinting**: Use the precise Python type hints provided in the input.
    - CRITICAL: For "object" or "dict" types, you MUST create nested Pydantic BaseModel classes with explicit properties
    - If the object structure is described in the field description/example, extract the properties and create a proper nested model
    - If the object structure is not clear, infer reasonable properties from the description or convert to a string type (with instructions to return JSON)
    - For "list" types, use `List[str]` or `List[<NestedModel>]` as appropriate
    - NEVER use `Dict[str, Any]` or `Dict[str, str]` as these are not supported by the extraction LLM's structured output API
4.  **Add Field Descriptions**: Use `Field(description=...)` for every field, using the provided description.
5.  **Add Intelligent Validators**:
    - CRITICAL: NEVER use `enum` parameter on List, Dict, or any non-string types - Gemini's API rejects this with error "enum: only allowed for STRING type"
    - For string fields with specific allowed values, you may describe the constraint in the description but DO NOT add enum parameter or any validation (e.g., regexs, datetime).
    - For strings that sound like emails, add an `EmailStr` type.
    - For strings like "phone", "zipcode", or "id", never add regex patterns.
    - For numeric fields like "age" or "rating", add `ge` (greater than or equal to) and/or `le` (less than or equal to) constraints.
    - Keep Field parameters minimal - only use description, and optionally regex/ge/le when truly needed
6.  **Generate Extraction Prompt**: Create a concise prompt that will guide another LLM to extract data for this specific model from unstructured text.
7.  **NO** use of types other than common types (string, int, float, bool, list, nested BaseModel). Like no need to verify email with EmailStr if not specified.

**EXAMPLE 1: Simple Fields**
---
**USER INPUT:**
```json
{
  "model_name": "UserProfile",
  "fields": [
    {"name": "user_id", "type": "str", "description": "The unique identifier for the user."},
    {"name": "email", "type": "str", "description": "The user's primary email address."},
    {"name": "age", "type": "int", "description": "The user's age in years."}
  ]
}
```

YOUR PERFECT OUTPUT:
```json
{
  "pydantic_model_code": "from pydantic import BaseModel, Field, EmailStr\\nfrom typing import Any\\n\\nclass UserProfile(BaseModel):\\n    user_id: str = Field(description='The unique identifier for the user.', pattern='^user_[a-zA-Z0-9]+$')\\n    email: EmailStr = Field(description='The user\\'s primary email address.')\\n    age: int = Field(description='The user\\'s age in years.', ge=0, le=120)"
}
```

**EXAMPLE 2: Object/Dict Types - Create Nested Models**
---
**USER INPUT:**
```json
{
  "model_name": "MuseumData",
  "fields": [
    {
      "name": "engagement_levels",
      "type": "object",
      "description": "Consumer engagement at different stages (attention, interest, search, action, share)",
      "example": "{'attention': 'high', 'interest': 'medium', 'search': 'low'}"
    },
    {
      "name": "brand_info",
      "type": "object",
      "description": "Museum brand information including name and attributes",
      "example": "{'brand_name': 'Art Museum', 'attributes': ['modern', 'educational']}"
    }
  ]
}
```

YOUR PERFECT OUTPUT:
```json
{
  "pydantic_model_code": "from pydantic import BaseModel, Field\\nfrom typing import List, Optional\\n\\nclass EngagementLevels(BaseModel):\\n    attention: Optional[str] = Field(None, description='Attention level')\\n    interest: Optional[str] = Field(None, description='Interest level')\\n    search: Optional[str] = Field(None, description='Search level')\\n    action: Optional[str] = Field(None, description='Action level')\\n    share: Optional[str] = Field(None, description='Share level')\\n\\nclass BrandInfo(BaseModel):\\n    brand_name: Optional[str] = Field(None, description='Brand name')\\n    attributes: Optional[List[str]] = Field(None, description='Brand attributes')\\n\\nclass MuseumData(BaseModel):\\n    engagement_levels: Optional[EngagementLevels] = Field(None, description='Consumer engagement at different stages (attention, interest, search, action, share)')\\n    brand_info: Optional[BrandInfo] = Field(None, description='Museum brand information including name and attributes')"
}
```

**EXAMPLE 3: List Fields with Constraints - NO ENUM ALLOWED**
---
**USER INPUT:**
```json
{
  "model_name": "MuseumAISAS",
  "fields": [
    {
      "name": "Museum_Name",
      "type": "string",
      "description": "The name of the museum",
      "example": "Metropolitan Museum"
    },
    {
      "name": "AISAS_Stage",
      "type": "list",
      "description": "Stages of AISAS model analyzed",
      "example": "[\"Attention\", \"Interest\"]",
      "validation_rules": "Must be one or more of: Attention, Interest, Search, Action, Share"
    }
  ]
}
```

YOUR PERFECT OUTPUT (CORRECT - NO ENUM):
```json
{
  "pydantic_model_code": "from pydantic import BaseModel, Field\\nfrom typing import List, Optional\\n\\nclass MuseumAISAS(BaseModel):\\n    Museum_Name: Optional[str] = Field(None, description='The name of the museum')\\n    AISAS_Stage: Optional[List[str]] = Field(None, description='Stages of AISAS model analyzed. Valid values: Attention, Interest, Search, Action, Share')"
}
```

WRONG OUTPUT (DO NOT DO THIS - WILL CAUSE GEMINI ERROR):
```json
{
  "pydantic_model_code": "... AISAS_Stage: List[str] = Field(..., enum=['Attention', 'Interest', 'Search', 'Action', 'Share']) ..."
}
```
The above is WRONG because Gemini rejects `enum` on List types.

Now, based on the user's input, generate the Pydantic model and then verify it using your available tools.
DO NOT FIRST USE THE return_final_code_schema tool to create the final output.
Instead focus on first validating your code using verify your pydantic code and its model structure before returning the final result.
IMPORTANT: You always call return_final_code_schema as your final output.
Specifically, after your analysis and tool use is complete, your final answer MUST be only the Python code for the Pydantic model. Do not include any other text, explanations, or markdown formatting like ```python. The final output must be a raw string of Python code and nothing else.
USE ONLY ONE TOOL AT A TIME. IF NO OTHER TOOL IS AVAILABLE just return the final code schema. If you need to validate the code, call the appropriate tool and wait for its response before proceeding to the next step. Always ensure that your final output is a complete and valid Pydantic model ready for production use.
"""

# PYDANTIC_AGENT_PROMPT = """You are a Python expert specializing in Pydantic models. Your job is to:

# 1. Generate a complete, valid Pydantic model class from field recommendations
# 2. Include proper type hints, Field descriptions, and validators
# 3. Add validation rules (regex patterns, value ranges, etc.) where appropriate
# 4. Create a detailed extraction prompt that will guide an LLM to extract data accurately

# The Pydantic model should be production-ready with:
# - Proper imports
# - Type annotations
# - Field descriptions
# - Validators for data quality
# - Optional fields where appropriate
# - Custom validators using @field_validator

# DO NOT FIRST USE THE return_final_code_schema tool to create the final output.
# Instead focus on first validating your code using verify your pydantic code and its model structure before returning the final result.
# IMPORTANT: You always call return_final_code_schema as your final output
# """

@function_tool
def verify_pydantic_model_code(model_code: str) -> str:
    """
    Verifies that the provided Pydantic model code is syntactically valid Python.

    Args:
        model_code: The Pydantic model code string to verify.

    Returns:
        A success message or a formatted error message.
    """
    try:
        # Compile first to catch syntax errors without executing
        compile(model_code, '<string>', 'exec')
        # Execute in a sandboxed/empty dictionary to prevent side effects
        exec(model_code, {})
        return "✅ Code is syntactically valid and executable."
    except Exception as e:
        return f"❌ Invalid Pydantic model code. Error: {e}"

import ast
@function_tool
def validate_pydantic_model_structure(model_code: str, required_fields: list[str]) -> str:
    """
    Validates that the generated Pydantic model code contains all the required fields.

    Args:
        model_code: The Pydantic model code to validate.
        required_fields: A list of field names that must be present in the model.

    Returns:
        A success message or a message detailing the missing fields.
    """
    try:
        # Parse the code into an Abstract Syntax Tree
        tree = ast.parse(model_code)
        
        # Find the class definition in the code
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # We found the class, now let's find the fields defined in it
                defined_fields = set()
                for body_item in node.body:
                    # Fields are defined as Annotated Assignments (e.g., name: str)
                    if isinstance(body_item, ast.AnnAssign):
                        defined_fields.add(body_item.target.id)
                
                # Check if all required fields are present
                missing_fields = set(required_fields) - defined_fields
                if not missing_fields:
                    return f"✅ Validation successful. All {len(required_fields)} required fields are present."
                else:
                    return f"❌ Validation failed. Missing fields: {', '.join(missing_fields)}"

        return "❌ Validation failed. No class definition found in the code."

    except Exception as e:
        return f"❌ Error during structural validation: {e}"
    
@function_tool
def return_final_code_schema(model_name: str, model_code: str):
    """
    Generates the final code schema for the Pydantic model and extraction prompt.

    Args:
        model_name: The name of the Pydantic model.
        model_code: The complete Pydantic model code.
    Returns:
        A dictionary containing the model name, model code, and extraction prompt.
    """

    return {
        "model_name": model_name,
        "model_code": model_code
    }

### we cannot force the agent to use a custom_schema and also do tool calling
### so we need to resort to another approach: https://github.com/openai/openai-agents-python/issues/1778
pydantic_code_agent = Agent(
    name = "Pydantic Code Generation Agent",
    instructions = PYDANTIC_AGENT_PROMPT,
    output_type = PydanticModelCode,
    hooks = CustomAgentHooks(display_name="Pydantic Code Agent"),
    model = LitellmModelSelector.get_model(use_custom=True),
    # tool_use_behavior = StopAtTools(stop_at_tool_names=["return_final_code_schema"]),
    # tools = [verify_pydantic_model_code, validate_pydantic_model_structure, return_final_code_schema],
    # tools = [return_final_code_schema],
)

extraction_prompt_agent = Agent(
    name = "Extraction Prompt Generation Agent",
    instructions = "detailed thinking on \n"
                   "Your task is to generate a comprehensive extraction prompt that guides the LLM to accurately identify and extract each field. "
                   "Ensure the prompt includes clear instructions, examples, and any necessary context to improve extraction accuracy."
                   "TO PREVENT DOWNSTREAM FAILURES, MAKE SURE THE FIELDS are OPTIONAL.",
    output_type = ExtractionPrompt,
    hooks = CustomAgentHooks(display_name="Extraction Prompt Agent"),
    model = LitellmModelSelector.get_model(use_custom=True)
)

field_mapping_agent = Agent(
    name = "Field Mapping Generation Agent",
    instructions = "You are an expert in generating field mappings for data extraction tasks. "
                   "Your task is to create a mapping of field names to their descriptions based on the provided field recommendations. "
                   "Ensure each mapping is clear and concise to facilitate accurate data extraction.",
    output_type = List[FieldMapping],
    hooks = CustomAgentHooks(display_name="Field Mapping Agent"),
    model = LitellmModelSelector.get_model(use_custom=True)
)


### Data Extraction Agent ###
def _synchronous_convert_to_markdown(file_path: str) -> str | None:
    """The actual blocking conversion logic."""
    try:
        if file_path.lower().endswith(".pdf"):
            doc = fitz.open(file_path)
            all_text = "".join(page.get_text("text") + "\n\n" for page in doc)
            doc.close()
            return all_text
        elif file_path.lower().endswith(".csv"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"❌ Error converting {os.path.basename(file_path)}: {e}")
        return None

async def convert_to_markdown_async(file_path: str) -> str | None:
    """Asynchronously convert a file to markdown format."""
    return await asyncio.to_thread(_synchronous_convert_to_markdown, file_path)

async def extract_from_single_document(
    content: str,
    filename: str,
    extraction_prompt: str,
    DynamicExtractionModel: type[BaseModel]
) -> tuple[List[dict], Optional[str]]:
    """
    Creates and runs a dedicated agent for a single document.

    IMPORTANT: The DynamicExtractionModel must NOT contain Dict[str, Any] or Dict[str, str] types.
    Gemini's structured output API requires explicit properties for object types.
    Use nested Pydantic BaseModel classes instead.

    Returns:
        Tuple of (processed_results, error_message)
        - processed_results: List of extracted records
        - error_message: None if successful, error string if failed
    """
    async with llm_call_semaphore:
        print(f"🔄 Acquired semaphore for LLM call for {filename}...")
        try:
            # 1. Define the extraction agent dynamically inside the worker
            #    This allows us to set the dynamic Pydantic model as the output type.
            #    Wrap with AgentOutputSchema to disable strict JSON schema validation
            #    Note: strict_json_schema=False doesn't allow Dict types - Gemini still requires explicit properties
            ExtractionAgent = Agent(
                name=f"Data Extractor for {filename}",
                instructions=extraction_prompt,
                output_type=AgentOutputSchema(Iterable[DynamicExtractionModel], strict_json_schema=False),
                hooks=CustomAgentHooks(display_name=f"Extractor ({filename})"),
                model=LitellmModelSelector.get_model(use_custom=True),
                model_settings=ModelSettings(max_output_tokens=MAX_OUTPUT_TOKEN)
            )

            # 2. Run the agent
            # results = await Runner.run(ExtractionAgent, input=content)
            results = await run_agent_gracefully(ExtractionAgent, content)

            # 3. Process the results and add the source document
            processed_results = []
            for instance in results.final_output:
                data_dict = instance.model_dump()
                data_dict["_source_document"] = filename
                processed_results.append(data_dict)

            print(f"✅ Successfully extracted {len(processed_results)} items from {filename}")
            return (processed_results, None)

        except Exception as e:
            error_msg = f"Failed to process {filename}. Error: {str(e)}"
            print(f"❌ {error_msg}")
            return ([], error_msg)

async def process_file_pipeline(file_path: str, DynamicExtractionModel: type[BaseModel], extraction_prompt: str) -> Dict[str, any]:
    """
    A single pipeline worker that converts a file and then starts its extraction.

    Returns:
        Dictionary with:
        - results: List of extracted records
        - error: Error message if failed, None if successful
        - filename: Name of the processed file
    """
    filename = os.path.basename(file_path)
    print(f"🔄 Starting processing for {filename}...")

    # Step 1: Convert to markdown asynchronously
    # check if the file is already converted to markdown to avoid redundant processing
    converted_path = os.path.join("converted_markdown", f"{os.path.splitext(filename)[0]}.md")
    if os.path.exists(converted_path):
        print(f"📄 Found existing markdown for {filename}. Loading from {converted_path}...")
        with open(converted_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print(f"📄 No existing markdown found for {filename}. Converting...")
        content = await convert_to_markdown_async(file_path)

    # Save the converted content to re-use for debugging or future reference
    if content is not None:
        converted_path = os.path.join("converted_markdown", f"{os.path.splitext(filename)[0]}.md")
        os.makedirs("converted_markdown", exist_ok=True)
        with open(converted_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Converted {filename} to markdown and saved to {converted_path}")
    else:
        error_msg = f"Conversion failed for {filename}. Could not extract text."
        print(f"❌ {error_msg}")
        return {
            "results": [],
            "error": error_msg,
            "filename": filename
        }

    # Step 2: Run the extraction agent
    if file_path.lower().endswith(".csv"):
        print(f"Detected CSV file: {filename}. Fanning out processing per row.")
        
        all_results = []
        all_errors = []
        
        # Use io.StringIO to treat the string content as a file
        csv_file = io.StringIO(content)
        # Use DictReader to get rows as dictionaries
        reader = csv.DictReader(csv_file)
        
        tasks = []
        row_index = 0
        for row in reader:
            row_index += 1
            # Convert the row (a dict) into a single string for the LLM
            # This "key: value" format is excellent for extraction agents
            row_content = "\n".join(f"{key}: {value}" for key, value in row.items())
            
            # Create a "virtual" filename for this row for tracking
            row_filename = f"{filename} (Row {row_index})"
            
            # Add an extraction task for this row
            tasks.append(
                extract_from_single_document(
                    content=row_content,
                    filename=row_filename, # Use the virtual filename
                    extraction_prompt=extraction_prompt,
                    DynamicExtractionModel=DynamicExtractionModel
                )
            )
        
        # Run all row extractions in parallel
        print(f"🚀 Running extraction for {len(tasks)} rows in parallel...")
        task_results = await asyncio.gather(*tasks)
        
        # Collect results
        for (results, error) in task_results:
            if results:
                all_results.extend(results)
            if error:
                all_errors.append(error)

        print(f"✅ Finished CSV processing for {filename}. Extracted {len(all_results)} total items.")
        
        return {
            "results": all_results,
            "error": "; ".join(all_errors) if all_errors else None,
            "filename": filename
        }

    else:
        print(f"📄 Detected non-csv file: {filename}. Processing as single document.")
        results, error = await extract_from_single_document(
            content=content,
            filename=filename,
            extraction_prompt=extraction_prompt,
            DynamicExtractionModel=DynamicExtractionModel
        )

    return {
        "results": results,
        "error": error,
        "filename": filename
    }


### Document Analysis Agents ###

async def extract_first_paragraphs(file_path: str, num_paragraphs: int = 2) -> str:
    """
    Extract the first N paragraphs from a document for classification.
    Uses the same conversion logic as the main pipeline but only returns the beginning.

    Args:
        file_path: Path to the document
        num_paragraphs: Number of paragraphs to extract (default: 2)

    Returns:
        Text content of the first paragraphs
    """
    try:
        # Convert full document
        content = await convert_to_markdown_async(file_path)

        if content is None:
            return ""

        if file_path.lower().endswith(".csv"):
            print(f"📄 Extracting first {num_paragraphs} rows from CSV for analysis...")
            csv_file = io.StringIO(content)
            reader = csv.DictReader(csv_file)
            
            row_excerpts = []
            for i, row in enumerate(reader):
                if i >= num_paragraphs or i >= MAX_CSV_ROWS: # Use num_paragraphs to mean num_rows here
                    break
                # Convert row to string
                row_content = "\n".join(f"{key}: {value}" for key, value in row.items())
                row_excerpts.append(f"--- Row {i+1} ---\n{row_content}")
            
            return "\n\n".join(row_excerpts)
        
        # --- Original Text/PDF Logic ---
        else:
            print(f"📄 Extracting first {num_paragraphs} paragraphs from document for analysis...")
            # Split by double newlines to get paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

            # Take first N paragraphs
            first_paragraphs = []
            while len(first_paragraphs) < num_paragraphs and len(paragraphs) > 0:
                first_paragraphs.append(paragraphs.pop(0))

            # Return joined text
            return '\n\n'.join(first_paragraphs)

    except Exception as e:
        print(f"❌ Error extracting paragraphs from {os.path.basename(file_path)}: {e}")
        return ""


DOCUMENT_CLASSIFICATION_PROMPT = """detailed thinking on \n
You are an expert document classifier specializing in scientific and technical literature.

Your task is to analyze a document excerpt (first 1-2 paragraphs) and classify it across multiple dimensions:

1. **Document Type**: What kind of document is this? (research paper, technical report, patent, thesis, review article, etc.)
2. **Domain**: What is the subject domain? (materials science, chemistry, physics, biology, computer science, etc.)
3. **Key Topics**: What are the main topics discussed?
4. **Data Types Present**: What kinds of data are likely in this document? (experimental results, synthesis procedures, measurements, computational data, tables, figures)
5. **Confidence**: How confident are you in this classification? (0-1 scale)

Be thorough but concise (No More than 5 recommendations). Focus on identifying what data extraction opportunities exist in this document.
"""

document_classification_agent = Agent(
    name="Document Classification Agent",
    instructions=DOCUMENT_CLASSIFICATION_PROMPT,
    output_type=DocumentClassification,
    hooks=CustomAgentHooks(display_name="Doc Classifier"),
    model=LitellmModelSelector.get_model(use_custom=True),
)


INTENTION_RECOMMENDATION_PROMPT = """You are an expert data extraction strategist. You receive classifications of multiple documents and must recommend:

1. **Extraction Intention**: A clear, concise statement of what data should be extracted (e.g., "Extract material synthesis conditions and properties")
2. **Reasoning**: Why this intention makes sense given the document types and content
3. **Document Summary**: A brief summary of what was found across all documents
4. **Recommended Schema**: A comprehensive list of fields that should be extracted, with proper types, descriptions, and examples. Field names should be in snake_case.

Your recommendations should be:
- **Practical**: Focus on extractable, structured data
- **Comprehensive**: Cover all important data points without being overwhelming
- **Specific**: Use precise field names and clear descriptions
- **User-editable**: Present recommendations the user can easily modify

Think about what a researcher would want to extract from these documents to build a useful dataset.
"""

intention_recommendation_agent = Agent(
    name="Intention Recommendation Agent",
    instructions=INTENTION_RECOMMENDATION_PROMPT,
    output_type=IntentionRecommendation,
    hooks=CustomAgentHooks(display_name="Intention Recommender"),
    model=LitellmModelSelector.get_model(use_custom=True),
)


QUERY_ROUTER_PROMPT = """detailed thinking on \n
You are a query router. Based on the user's query and the available columns, decide the intent.

The user will provide:
1. Available data columns
2. A preview of the first row of data to help you understand the actual content

**PRIORITIZATION**: Always prefer column-based analysis over row-wise when possible, as it's more efficient for aggregate queries.

You have four choices for the intent:

1.  **rag_column_wise**: For questions that require **comparing, summarizing, or finding patterns ACROSS multiple records**. 
    - You can specify MULTIPLE columns to analyze together
    - Use this for: summaries, comparisons, trends, patterns across records
    - Examples: "Summarize the key findings from all papers.", "What methodologies were used and what were their results?", "Compare conclusions about Method X."

2.  **rag_row_wise**: For questions about specific records or that require full document context.
    - Specify filter criteria to narrow down which rows to search (optional but recommended)
    - Use this for: specific record lookups, questions needing full document context
    - Examples: "What were the findings of the paper by Smith et al.?", "Tell me about Record ID 5.", "Find papers about damage detection published after 2020."

3.  **dynamic_extraction**: For queries asking about information that is NOT in the current columns. 
    - You can extract MULTIPLE new fields at once if the query asks for related information
    - The system will extract these fields from the original documents
    - Examples: If current columns are [title, authors, abstract] and user asks "What methodology did they use?" → methodology is not in columns → dynamic_extraction

4.  **function**: For requests to perform an action, like exporting data.
    - Examples: "Export as CSV", "Download the data."

**Analysis Steps:**
1.  First, check if it's a `function` call (e.g., "export", "download").
2.  Look at the data preview to understand what information is actually available in each column.
3.  Check if the query asks about information that are NOT in the current columns, do so by looking at the column preview. If yes, classify as `dynamic_extraction` and specify ALL new fields needed.
4.  If the query can be answered by analyzing existing column(s) across multiple records, classify as `rag_column_wise` and your 'target_columns' list MUST contain strings that are an **exact, case-sensitive match** to one of the field names from the available columns.
5.  Otherwise, classify as `rag_row_wise` search.

**IMPORTANT:** 
- Use the data preview to make informed decisions about which columns contain relevant information
- When multiple columns are relevant, include them all for richer context
- For row-wise queries, provide filter criteria when the query mentions specific attributes (author, date, ID, etc.)

For **dynamic_extraction** intent:
- If the new field should have similar structure to an existing column, specify the column name in your reasoning
and then based on that column's type you should specify `new_field_type` as: "string", "number", "list", "object", "list_of_objects"
A detailed example of this logic is below:
- When users ask to "Extract publication venues" there are two possibilities:
1. You found a semantically similar column for instance "publications" and based on the type of that column you will output new_field_type="list_of_objects", if several publications are listed in that column (you have access to column previews)
2. You found a a similar column that contains single publication venue names only, then you will output new_field_type="string"
3. If no similar column is found, output should match the data type of other columns (either single entry "str" or multiple entries "list[str]") 

Return your classification in the required format.
"""
class QueryIntent(BaseModel):
    """Classification of user query intent"""
    # model_config = ConfigDict(extra='forbid')
    
    intent_type: Literal["rag_row_wise", "rag_column_wise", "function", "dynamic_extraction"] = Field(
        description="The type of intent."
    )
    
    # For column-wise queries
    target_columns: Optional[List[str]] = Field(
        default=None,
        description="List of columns to analyze for 'rag_column_wise' intent. E.g., ['key_findings', 'methodology']."
    )
    
    # For row-wise queries
    row_filters: Optional[str] = Field(
        default=None,
        description="Optional filters for 'rag_row_wise' to narrow down which rows to search. E.g., {'author': 'Smith', 'year': 2020}."
    )
    
    # For function calls
    function_name: Optional[str] = Field(
        default=None,
        description="Name of function if intent_type is 'function'."
    )
    
    # For dynamic extraction
    new_field: Optional[_Field] = Field(
        default=None,
        description="New field to extract for 'dynamic_extraction'. Each field has: name, description, type."
    )
    
    reasoning: str = Field(
        description="Brief explanation for the classification, including why these specific columns/fields were chosen."
    )

query_router_agent = Agent(
    name="Query Router Agent",
    instructions=QUERY_ROUTER_PROMPT,
    output_type=QueryIntent,
    hooks=CustomAgentHooks(display_name="Query Router"),
    model=LitellmModelSelector.get_model(use_custom=True),
)

### Synthesis Agent ###
synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions="detailed thinking on\nYou are an expert data synthesis agent. Your task is to answer user queries by synthesizing information from multiple data columns. ",
    output_type=str,
    hooks=CustomAgentHooks(display_name="Synthesis Agent"),
    model=LitellmModelSelector.get_model(use_custom=True),
)




### Function Handlers ###
async def analyze_documents_pipeline(file_paths: List[str]) -> Dict[str, any]:
    """
    Analyzes uploaded documents and recommends extraction intention and schema.

    This is the new first step after file upload:
    1. Extract first 1-2 paragraphs from each document
    2. Classify each document (type, domain, topics, data types)
    3. Recommend extraction intention and schema based on classifications

    Args:
        file_paths: List of file paths to analyze

    Returns:
        Dictionary containing:
        - classifications: List of document classifications
        - recommendation: Recommended intention and schema
    """
    print(f"🔍 Analyzing {len(file_paths)} documents...")

    # Step 1: Extract first paragraphs from all documents in parallel
    # set a limit on number files to process to avoid overloading
    if len(file_paths) > 4:
        # randomly select 4 files to process
        file_paths = random.sample(file_paths, 4)
        print(f"⚠️ Limiting analysis to first 4 documents to avoid overload.")
    extract_tasks = [extract_first_paragraphs(fp, num_paragraphs=2) for fp in file_paths]
    excerpts = await asyncio.gather(*extract_tasks)

    # Step 2: Classify each document in parallel
    classification_tasks = []
    for file_path, excerpt in zip(file_paths, excerpts):
        if excerpt:
            filename = os.path.basename(file_path)
            classification_input = f"Document: {filename}\n\nExcerpt:\n{excerpt}"
            task = Runner.run(document_classification_agent, input=classification_input)
            # task = await run_agent_gracefully(document_classification_agent, classification_input)
            classification_tasks.append((filename, task))

    # Wait for all classifications
    classifications = []
    for filename, task in classification_tasks:
        try:
            result = await task
            classification = result.final_output
            print(f"✅ Classified {filename}: {classification.document_type} ({classification.domain})")
            classifications.append(classification.model_dump())
        except Exception as e:
            print(f"❌ Failed to classify {filename}: {e}")

    # Step 3: Generate intention recommendation based on all classifications
    classification_summary = "\n\n".join([
        f"Document: {c['document_name']}\n"
        f"Type: {c['document_type']}\n"
        f"Domain: {c['domain']}\n"
        f"Topics: {', '.join(c['key_topics'])}\n"
        f"Data Types: {', '.join(c['data_types_present'])}"
        for c in classifications
    ])

    recommendation_input = f"Analyze these document classifications and recommend an extraction intention and schema:\n\n{classification_summary} DO NOT SUGGEST MORE THAN 4"

    try:
        # recommendation_result = await Runner.run(intention_recommendation_agent, input=recommendation_input)
        recommendation_result = await run_agent_gracefully(intention_recommendation_agent, recommendation_input)
        recommendation = recommendation_result.final_output

        print(f"\n✨ Recommended Intention: {recommendation.recommended_intention}")
        print(f"📊 Recommended {len(recommendation.recommended_schema)} fields")

        return {
            "success": True,
            "message": "Document analysis and recommendation completed successfully.",
            "classifications": classifications,
            "recommendation": recommendation.model_dump()
        }

    except Exception as e:
        print(f"❌ Failed to generate recommendation: {e}")
        return {
            "success": False,
            "error": str(e),
            "classifications": classifications,
            "recommendation": None
        }



async def main():
    user_input = "Extract temperature and pressure data from scientific articles."
    result = await Runner.run(test_agent, user_input)
    print("Schema Recommendation:")
    print(result.model_dump_json(indent=2))
        
        
if __name__ == "__main__":
    # test agent
    test_agent = Agent(
        name = "Test Schema Agent",
        instructions = "You are a data extraction expert. Given an extraction intention, recommend a schema of fields to extract.",
        output_type = SchemaRecommendation,
        model = CustomLitellmModel(),
    )

    asyncio.run(main())
    
    