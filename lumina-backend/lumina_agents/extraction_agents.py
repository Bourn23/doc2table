"""
Extraction Agents Module

This module contains document processing and data extraction pipeline functionality.
It handles file conversion (PDF, CSV, text) to markdown format and orchestrates
the extraction of structured data from documents using AI agents.

Key Components:
- File conversion functions for various formats
- Single document extraction pipeline
- Multi-document parallel processing with concurrency control
- CSV row-by-row processing
"""

import asyncio
import csv
import io
import os
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel

import fitz  # PyMuPDF for PDF processing

from lumina_agents.config import (
    LitellmModelSelector,
    CustomAgentHooks,
    MAX_OUTPUT_TOKEN,
    llm_call_semaphore,
)
from shared.utils import run_agent_gracefully

from agents import Agent, AgentOutputSchema, ModelSettings
from typing import Iterable


# Constants
MAX_CSV_ROWS = 20  # Maximum number of rows to process per CSV file for initial screening


def _synchronous_convert_to_markdown(file_path: str) -> Optional[str]:
    """
    Synchronously convert a file to markdown/text format.
    
    This is the actual blocking conversion logic that handles different file types:
    - PDF files: Extracts text using PyMuPDF
    - CSV files: Reads as plain text
    - Other files: Reads as plain text
    
    Args:
        file_path: Path to the file to convert
        
    Returns:
        Extracted text content, or None if conversion fails
        
    Example:
        >>> content = _synchronous_convert_to_markdown("document.pdf")
        >>> if content:
        ...     print(f"Extracted {len(content)} characters")
    """
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


async def convert_to_markdown_async(file_path: str) -> Optional[str]:
    """
    Asynchronously convert a file to markdown format.
    
    This function wraps the synchronous conversion logic to run in a thread pool,
    allowing for non-blocking file I/O operations.
    
    Args:
        file_path: Path to the file to convert
        
    Returns:
        Extracted text content, or None if conversion fails
        
    Example:
        >>> content = await convert_to_markdown_async("document.pdf")
        >>> if content:
        ...     print("Conversion successful")
    """
    return await asyncio.to_thread(_synchronous_convert_to_markdown, file_path)


async def extract_from_single_document(
    content: str,
    filename: str,
    extraction_prompt: str,
    DynamicExtractionModel: type[BaseModel]
) -> Tuple[List[dict], Optional[str]]:
    """
    Extract structured data from a single document using an AI agent.
    
    Creates and runs a dedicated extraction agent for the document, using the provided
    Pydantic model to structure the output. The agent is configured with semaphore-based
    concurrency control to prevent overwhelming the LLM API.
    
    IMPORTANT: The DynamicExtractionModel must NOT contain Dict[str, Any] or Dict[str, str] types.
    Gemini's structured output API requires explicit properties for object types.
    Use nested Pydantic BaseModel classes instead.
    
    Args:
        content: The text content to extract from
        filename: Name of the source file (for tracking and metadata)
        extraction_prompt: Instructions for the extraction agent
        DynamicExtractionModel: Pydantic model defining the extraction schema
        
    Returns:
        Tuple of (processed_results, error_message):
        - processed_results: List of extracted records as dictionaries
        - error_message: None if successful, error string if failed
        
    Example:
        >>> from pydantic import BaseModel, Field
        >>> class Paper(BaseModel):
        ...     title: str = Field(description="Paper title")
        ...     authors: List[str] = Field(description="List of authors")
        >>> 
        >>> results, error = await extract_from_single_document(
        ...     content="Title: AI Research\\nAuthors: Smith, Jones",
        ...     filename="paper.txt",
        ...     extraction_prompt="Extract paper metadata",
        ...     DynamicExtractionModel=Paper
        ... )
    """
    async with llm_call_semaphore:
        print(f"🔄 Acquired semaphore for LLM call for {filename}...")
        try:
            # Define the extraction agent dynamically with the provided Pydantic model
            # Wrap with AgentOutputSchema to disable strict JSON schema validation
            # Note: strict_json_schema=False doesn't allow Dict types - Gemini still requires explicit properties
            ExtractionAgent = Agent(
                name=f"Data Extractor for {filename}",
                instructions=extraction_prompt,
                output_type=AgentOutputSchema(Iterable[DynamicExtractionModel], strict_json_schema=False),
                hooks=CustomAgentHooks(display_name=f"Extractor ({filename})"),
                model=LitellmModelSelector.get_model(use_custom=True),
                model_settings=ModelSettings(max_output_tokens=MAX_OUTPUT_TOKEN)
            )

            # Run the agent with graceful error handling
            results = await run_agent_gracefully(ExtractionAgent, content)

            # Process the results and add the source document metadata
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


async def process_file_pipeline(
    file_path: str,
    DynamicExtractionModel: type[BaseModel],
    extraction_prompt: str
) -> Dict[str, Any]:
    """
    Complete pipeline for processing a single file: conversion and extraction.
    
    This function orchestrates the entire extraction workflow:
    1. Checks for cached markdown conversion
    2. Converts file to markdown if needed
    3. Saves converted content for reuse
    4. Handles CSV files with row-by-row parallel processing
    5. Handles other files as single documents
    
    CSV files are processed row-by-row in parallel, with each row treated as a
    separate document. This allows for efficient extraction from large CSV files.
    
    Args:
        file_path: Path to the file to process
        DynamicExtractionModel: Pydantic model defining the extraction schema
        extraction_prompt: Instructions for the extraction agent
        
    Returns:
        Dictionary containing:
        - results: List of extracted records
        - error: Error message if failed, None if successful
        - filename: Name of the processed file
        
    Example:
        >>> result = await process_file_pipeline(
        ...     file_path="/data/papers/research.pdf",
        ...     DynamicExtractionModel=PaperModel,
        ...     extraction_prompt="Extract paper metadata"
        ... )
        >>> print(f"Extracted {len(result['results'])} records")
    """
    filename = os.path.basename(file_path)
    print(f"🔄 Starting processing for {filename}...")

    # Step 1: Convert to markdown asynchronously
    # Check if the file is already converted to markdown to avoid redundant processing
    converted_path = os.path.join("converted_markdown", f"{os.path.splitext(filename)[0]}.md")
    if os.path.exists(converted_path):
        print(f"📄 Found existing markdown for {filename}. Loading from {converted_path}...")
        with open(converted_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print(f"📄 No existing markdown found for {filename}. Converting...")
        content = await convert_to_markdown_async(file_path)

    # Save the converted content to reuse for debugging or future reference
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
                    filename=row_filename,
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
        print(f"📄 Detected non-CSV file: {filename}. Processing as single document.")
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


async def extract_first_paragraphs(file_path: str, num_paragraphs: int = 2) -> str:
    """
    Extract the first N paragraphs from a document for classification or preview.
    
    Uses the same conversion logic as the main pipeline but only returns the beginning
    of the document. This is useful for document classification without processing
    the entire file.
    
    For CSV files, extracts the first N rows instead of paragraphs.
    
    Args:
        file_path: Path to the document
        num_paragraphs: Number of paragraphs (or rows for CSV) to extract (default: 2)
        
    Returns:
        Text content of the first paragraphs/rows, or empty string if extraction fails
        
    Example:
        >>> excerpt = await extract_first_paragraphs("paper.pdf", num_paragraphs=3)
        >>> print(f"Preview: {excerpt[:100]}...")
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
                if i >= num_paragraphs or i >= MAX_CSV_ROWS:
                    break
                # Convert row to string
                row_content = "\n".join(f"{key}: {value}" for key, value in row.items())
                row_excerpts.append(f"--- Row {i+1} ---\n{row_content}")
            
            return "\n\n".join(row_excerpts)
        
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
        error_msg = f"Error extracting paragraphs from {os.path.basename(file_path)}: {e}"
        print(f"❌ {error_msg}")
        return ""
