"""
Document Analysis Agents Module

This module contains agents and pipelines for analyzing documents to classify their
content and recommend extraction intentions and schemas.

Components:
- DocumentClassification: Pydantic model for document classification results
- IntentionRecommendation: Pydantic model for extraction intention recommendations
- document_classification_agent: Agent that classifies document types and content
- intention_recommendation_agent: Agent that recommends extraction strategies
- extract_first_paragraphs: Utility to extract document excerpts for analysis
- analyze_documents_pipeline: Complete pipeline for document analysis and recommendation
"""

from agents import Agent, Runner
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import asyncio
import csv
import io
import os
import random

from lumina_agents.config import (
    LitellmModelSelector,
    CustomAgentHooks,
    MAX_CSV_ROWS
)
from lumina_agents.extraction_agents import convert_to_markdown_async
from shared.utils import run_agent_gracefully


# ============================================================================
# Pydantic Models
# ============================================================================

class FieldRecommendation(BaseModel):
    """Recommended field for extraction"""
    field_name: str = Field(description="Name of the field to extract")
    description: str = Field(description="What this field represents")
    data_type: str = Field(description="Expected data type (string, number, boolean, list, etc.)")
    unit: Optional[str] = Field(default=None, description="Unit of measurement if applicable")
    example: str = Field(description="Example of what this field might contain")
    validation_rules: Optional[str] = Field(default=None, description="Any validation constraints")


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
    confidence: float = Field(description="Confidence score for recommendation (0-1)")


# ============================================================================
# Agent Definitions
# ============================================================================

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


# ============================================================================
# Pipeline Functions
# ============================================================================

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
                if i >= num_paragraphs or i >= MAX_CSV_ROWS:  # Use num_paragraphs to mean num_rows here
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
        - success: Boolean indicating if analysis succeeded
        - message: Success message or None
        - error: Error message or None
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
