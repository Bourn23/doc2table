"""
Schema Generation Agents Module

This module contains AI agents and Pydantic models for schema generation and
Pydantic model code creation. These agents work together to:
1. Recommend extraction schemas based on user intentions
2. Generate production-ready Pydantic model code
3. Create extraction prompts for data extraction agents
4. Generate field mappings for data extraction

The schema generation pipeline:
- schema_agent: Recommends fields to extract based on user intention
- pydantic_code_agent: Converts field recommendations into Pydantic model code
- extraction_prompt_agent: Creates detailed prompts for extraction agents
- field_mapping_agent: Generates field name to description mappings
"""

from agents import Agent, function_tool
from typing import List, Optional
from pydantic import BaseModel, Field
from lumina_agents.config import LitellmModelSelector, CustomAgentHooks
from lumina_agents.tools import verify_pydantic_model_code, validate_pydantic_model_structure, return_final_code_schema
from shared.tools import SchemaRecommendation


# ============================================================================
# Pydantic Models for Schema Generation
# ============================================================================

class FieldMapping(BaseModel):
    """Mapping of field name to its description"""
    field_name: str = Field(description="Name of the field")
    description: str = Field(description="Description of the field")


class PydanticModelCode(BaseModel):
    """Generated Pydantic model code"""
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: str = Field(description="Complete Pydantic model code")


class ExtractionPrompt(BaseModel):
    """Extraction prompt for guiding data extraction agents"""
    prompt_text: str = Field(description="Detailed prompt for extraction agent")


class ExtractionSchema(BaseModel):
    """Generated extraction schema with Pydantic model"""
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: PydanticModelCode = Field(description="Complete Pydantic model code")
    extraction_prompt: ExtractionPrompt = Field(description="Detailed prompt for extraction agent")
    field_mappings: List[FieldMapping] = Field(description="Mapping of field names to descriptions")


class ExtractionSchemaUpdated(BaseModel):
    """Updated extraction schema with Pydantic model"""
    model_name: str = Field(description="Name of the Pydantic model")
    model_code: PydanticModelCode = Field(description="Complete Pydantic model code")
    extraction_prompt: ExtractionPrompt = Field(description="Detailed prompt for extraction agent")
    field_mappings: List[FieldMapping] = Field(description="Mapping of field names to descriptions")


# ============================================================================
# Schema Generation Agent
# ============================================================================

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
    name="Schema Generation Agent",
    instructions=SCHEMA_AGENT_PROMPT,
    output_type=SchemaRecommendation,
    model=LitellmModelSelector.get_model(use_custom=True),
)


# ============================================================================
# Pydantic Code Generation Agent
# ============================================================================

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
      "example": "[\\"Attention\\", \\"Interest\\"]",
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

pydantic_code_agent = Agent(
    name="Pydantic Code Generation Agent",
    instructions=PYDANTIC_AGENT_PROMPT,
    output_type=PydanticModelCode,
    hooks=CustomAgentHooks(display_name="Pydantic Code Agent"),
    model=LitellmModelSelector.get_model(use_custom=True),
)


# ============================================================================
# Extraction Prompt Generation Agent
# ============================================================================

extraction_prompt_agent = Agent(
    name="Extraction Prompt Generation Agent",
    instructions="detailed thinking on \n"
                   "Your task is to generate a comprehensive extraction prompt that guides the LLM to accurately identify and extract each field. "
                   "Ensure the prompt includes clear instructions, examples, and any necessary context to improve extraction accuracy."
                   "TO PREVENT DOWNSTREAM FAILURES, MAKE SURE THE FIELDS are OPTIONAL.",
    output_type=ExtractionPrompt,
    hooks=CustomAgentHooks(display_name="Extraction Prompt Agent"),
    model=LitellmModelSelector.get_model(use_custom=True)
)


# ============================================================================
# Field Mapping Generation Agent
# ============================================================================

field_mapping_agent = Agent(
    name="Field Mapping Generation Agent",
    instructions="You are an expert in generating field mappings for data extraction tasks. "
                   "Your task is to create a mapping of field names to their descriptions based on the provided field recommendations. "
                   "Ensure each mapping is clear and concise to facilitate accurate data extraction.",
    output_type=List[FieldMapping],
    hooks=CustomAgentHooks(display_name="Field Mapping Agent"),
    model=LitellmModelSelector.get_model(use_custom=True)
)
