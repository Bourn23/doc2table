from typing import List, Dict, Any, Optional
# import BaseModel from pydantic
from pydantic import BaseModel, Field


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================
class _Field(BaseModel):
    name: str
    type: str
    description: str
    
class FunctionResult(BaseModel):
    success: bool
    message: str
    
    filepath: Optional[str] = None      # <-- The crucial field!
    s3_key: Optional[str] = None     # S3 key if uploaded to S3
    record_count: Optional[int] = None
    
    field_name: Optional[str] = None    # For your dynamic extraction results
    records_updated: Optional[int] = None
    sample_values: Optional[List[Any]] = None
    
    new_field: Optional[_Field] = None
    new_records: Optional[List[Dict[str, Any]]] = None
    new_job_id: Optional[str] = None
    
class QueryRequest(BaseModel):
    session_id: int
    query: str
    num_results: int = 5

class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    confidence: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None
    relevant_records: Optional[List[Dict[str, Any]]] = None
    result_type: str = "rag"  # "rag" or "function"
    # function_result: Optional[Dict[str, Any]] = None  # For function execution results
    function_result: Optional[FunctionResult] = None  # For function execution results

class ExtractionRequest(BaseModel):
    intention: str  # What the user wants to extract

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_ids: List[str]
    total_files: int

class IndexResponse(BaseModel):
    success: bool
    message: str
    indexed_count: int

class IndexRequest(BaseModel):
    session_id: int
    
class ExtractionResponse(BaseModel):
    success: bool
    message: str
    records: List[Dict[str, Any]]
    total_records: int
    errors: Optional[List[Dict[str, str]]] = None  # List of {filename, error}

class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    classifications: List[Dict[str, Any]]
    recommendation: Dict[str, Any]

class UpdateSchemaRequest(BaseModel):
    session_id: int
    intention: str
    fields: List[Dict[str, Any]]  # User-edited fields
    
class InitiateUploadRequest(BaseModel):
    filenames: list[str]

class InitiateUploadResponse(BaseModel):
    success: bool
    session_id: int
    
#===========================================================================#
# Pydantic Models for Extraction Schema
#===========================================================================#    
class AnalyzeRequest(BaseModel):
    session_id: int
    job_id: str
    
class ExtractionRequest(BaseModel):
    session_id: int
    intention: str

class MaxRetriesExceededError(Exception):
    """Exception raised when a function fails after all retry attempts."""
    pass


#===========================================================================#
# Dynamic Column Addition Models
#===========================================================================#
class DynamicColumnJobRequest(BaseModel):
    """
    Defines the payload for starting a dynamic column extraction job.
    """
    job_id: str
    session_id: int
    field_name: str
    field_description: str
    field_type: str = "string"
    examples: Optional[List[str]] = None
    
class DynamicColumnResponse(BaseModel):
    success: bool
    field_name: str
    records_updated: int
    sample_values: List[Any]
    message: str
    new_field: _Field
    new_records: Optional[List[Dict[str, Any]]] = None
    
class ExtractionJobRequest(BaseModel):
    session_id: int
    intention: str
    job_id: str
    
    
class IndexJobRequest(BaseModel):
    session_id: int
    job_id: str


#===========================================================================#
# Pydantic Models for Graph Generation
#===========================================================================#
class GraphGenerationRequest(BaseModel):
    """Request model for generating a knowledge graph from query results."""
    relevant_records: List[Dict[str, Any]] = Field(
        ...,
        description="A list of relevant records returned by the /query endpoint."
    )
    query_id: str

class NodeModel(BaseModel):
    id: str
    type: str
    properties: Dict[str, Any] = {}

class RelationshipModel(BaseModel):
    source: NodeModel
    target: NodeModel
    type: str
    properties: Dict[str, Any] = {}

class GraphGenerationResponse(BaseModel):
    """Response model containing the generated graph data."""
    success: bool
    message: str
    nodes: List[NodeModel]
    relationships: List[RelationshipModel]