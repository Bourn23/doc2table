"""
Query Agents Module

This module contains agents responsible for query routing and answer synthesis.
It includes:
- QueryIntent: Pydantic model for query classification
- query_router_agent: Routes queries to appropriate handlers
- synthesis_agent: Synthesizes answers from multiple sources
"""

from agents import Agent
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from lumina_agents.config import LitellmModelSelector, CustomAgentHooks
from shared.api_types import _Field


# Pydantic Models

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


# Agent Prompts

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


# Agent Definitions

query_router_agent = Agent(
    name="Query Router Agent",
    instructions=QUERY_ROUTER_PROMPT,
    output_type=QueryIntent,
    hooks=CustomAgentHooks(display_name="Query Router"),
    model=LitellmModelSelector.get_model(use_custom=True),
)

synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions="detailed thinking on\nYou are an expert data synthesis agent. Your task is to answer user queries by synthesizing information from multiple data columns. ",
    output_type=str,
    hooks=CustomAgentHooks(display_name="Synthesis Agent"),
    model=LitellmModelSelector.get_model(use_custom=True),
)
