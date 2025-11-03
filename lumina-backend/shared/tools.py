from agents import function_tool
from typing import List, Optional
from pydantic import BaseModel, Field


## Schema generation agent
class FieldRecommendation(BaseModel):
    """Recommended field for extraction"""
    field_name: str = Field(description="Name of the field to extract")
    description: str = Field(description="What this field represents")
    data_type: str = Field(description="Expected data type (string, number, boolean, list, etc.)")
    unit: Optional[str] = Field(default=None, description="Unit of measurement if applicable")
    example: str = Field(description="Example of what this field might contain")
    validation_rules: Optional[str] = Field(default=None, description="Any validation constraints")

class SchemaRecommendation(BaseModel):
    """Complete schema recommendation"""
    extraction_goal: str = Field(description="User's extraction intention")
    recommended_schema: List[FieldRecommendation]
    additional_notes: str = Field(description="Additional guidance for extraction")

## Document Classification Models
class DocumentClassification(BaseModel):
    """Classification of a document based on its content"""
    document_name: str = Field(description="Name of the document")
    document_type: str = Field(description="Type of document (e.g., research paper, technical report, patent, thesis)")
    domain: List[str] = Field(description="Subject domain (e.g., materials science, chemistry, biology, computer science)")
    key_topics: List[str] = Field(description="Main topics discussed in the document")
    data_types_present: List[str] = Field(description="Types of data found (e.g., experimental data, synthesis procedures, measurements, tables)")
    confidence: float = Field(description="Confidence score for classification (0-1)", ge=0, le=1)

class IntentionRecommendation(BaseModel):
    """AI-recommended intention and schema based on document analysis"""
    recommended_intention: str = Field(description="Recommended extraction intention based on document classifications")
    reasoning: str = Field(description="Why this intention was recommended")
    document_summary: str = Field(description="Brief summary of what was found across all documents")
    recommended_schema: List[FieldRecommendation] = Field(description="Recommended fields to extract")
    confidence: float = Field(description="Confidence score for recommendation (0-1)")#, ge=0, le=1)

