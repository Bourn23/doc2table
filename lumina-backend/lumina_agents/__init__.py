"""
Lumina Agents Package

This package contains all AI agent-related code for the Lumina document processing system.
It provides a modular, well-organized structure for schema generation, data extraction,
document analysis, query processing, and RAG (Retrieval-Augmented Generation) functionality.

Main Components:
    - config: Model configuration, API clients, and selection utilities
    - tools: Reusable tool functions for agent validation and processing
    - schema_agents: Schema generation and Pydantic model creation agents
    - extraction_agents: Document processing and data extraction pipeline
    - analysis_agents: Document classification and intention recommendation
    - query_agents: Query routing and answer synthesis
    - rag_agent: Complete RAG system for retrieval and generation

Quick Start:
    >>> from lumina_agents import schema_agent, process_file_pipeline, RAGSystem
    >>> 
    >>> # Generate a schema
    >>> result = await schema_agent.run("Extract author names and publication dates")
    >>> 
    >>> # Process documents
    >>> extracted = await process_file_pipeline(
    ...     file_path="document.pdf",
    ...     DynamicExtractionModel=MyModel,
    ...     extraction_prompt="Extract key information"
    ... )
    >>> 
    >>> # Query with RAG
    >>> rag = RAGSystem(embed_key, rerank_key, gemini_key)
    >>> rag.index_documents(chunks)
    >>> answer = rag.run_pipeline("What are the main findings?")

For detailed documentation, see individual module docstrings.
"""

# ============================================================================
# Configuration and Utilities
# ============================================================================

from .config import (
    # Model instances
    gemini_model,
    gemini_model_lite,
    nvidia_nim_model,
    nvidia_nim_model_large,
    
    # Utilities
    LitellmModelSelector,
    CustomAgentHooks,
    
    # Constants
    MAX_OUTPUT_TOKEN,
    MAX_CSV_ROWS,
    LLM_CALL_LIMIT,
    llm_call_semaphore,
)

# ============================================================================
# Tools
# ============================================================================

from .tools import (
    verify_pydantic_model_code,
    validate_pydantic_model_structure,
    return_final_code_schema,
)

# ============================================================================
# Schema Generation Agents
# ============================================================================

from .schema_agents import (
    # Agents
    schema_agent,
    pydantic_code_agent,
    extraction_prompt_agent,
    field_mapping_agent,
    
    # Pydantic Models
    SchemaRecommendation,
    PydanticModelCode,
    ExtractionPrompt,
    FieldMapping,
    ExtractionSchema,
    ExtractionSchemaUpdated,
)

# ============================================================================
# Extraction Agents
# ============================================================================

from .extraction_agents import (
    # Pipeline functions
    process_file_pipeline,
    extract_from_single_document,
    
    # Utility functions
    convert_to_markdown_async,
    extract_first_paragraphs,
)

# ============================================================================
# Analysis Agents
# ============================================================================

from .analysis_agents import (
    # Agents
    document_classification_agent,
    intention_recommendation_agent,
    
    # Pipeline functions
    analyze_documents_pipeline,
    
    # Pydantic Models
    DocumentClassification,
    IntentionRecommendation,
    FieldRecommendation,
)

# ============================================================================
# Query Agents
# ============================================================================

from .query_agents import (
    # Agents
    query_router_agent,
    synthesis_agent,
    
    # Pydantic Models
    QueryIntent,
)

# ============================================================================
# RAG System
# ============================================================================

from .rag_agent import (
    RAGSystem,
)

# ============================================================================
# Package Metadata
# ============================================================================

__version__ = "1.0.0"
__author__ = "Lumina Team"

__all__ = [
    # Configuration
    "gemini_model",
    "gemini_model_lite",
    "nvidia_nim_model",
    "nvidia_nim_model_large",
    "LitellmModelSelector",
    "CustomAgentHooks",
    "MAX_OUTPUT_TOKEN",
    "MAX_CSV_ROWS",
    "LLM_CALL_LIMIT",
    "llm_call_semaphore",
    
    # Tools
    "verify_pydantic_model_code",
    "validate_pydantic_model_structure",
    "return_final_code_schema",
    
    # Schema Agents
    "schema_agent",
    "pydantic_code_agent",
    "extraction_prompt_agent",
    "field_mapping_agent",
    "SchemaRecommendation",
    "PydanticModelCode",
    "ExtractionPrompt",
    "FieldMapping",
    "ExtractionSchema",
    "ExtractionSchemaUpdated",
    
    # Extraction Agents
    "process_file_pipeline",
    "extract_from_single_document",
    "convert_to_markdown_async",
    "extract_first_paragraphs",
    
    # Analysis Agents
    "document_classification_agent",
    "intention_recommendation_agent",
    "analyze_documents_pipeline",
    "DocumentClassification",
    "IntentionRecommendation",
    "FieldRecommendation",
    
    # Query Agents
    "query_router_agent",
    "synthesis_agent",
    "QueryIntent",
    
    # RAG System
    "RAGSystem",
]
