import logging
import traceback
import asyncio
import re
import ast
import json
from typing import List, Optional, Dict, Any, Type, Literal

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


# Import shared components
import shared.models as models
from shared.database import get_async_db
from shared.job_manager import JobStatusManager
from shared.api_types import (
    AnalyzeRequest, AnalyzeResponse, UpdateSchemaRequest,
    ExtractionJobRequest, ExtractionResponse, DynamicColumnJobRequest,
    DynamicColumnResponse, MaxRetriesExceededError 
)

# Import agent pipelines (assuming this module is accessible)
from shared.agents_collection import (
    schema_agent,
    analyze_documents_pipeline,
    process_file_pipeline,
    pydantic_code_agent,
    extraction_prompt_agent,
    PydanticModelCode
)

# Pydantic and typing imports for dynamic model creation
import pydantic
from pydantic import BaseModel
from shared.utils import run_agent_gracefully

# ============================================================================
# Service Setup
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sets the concurrent file processing limit to 4
EXTRACTION_CONCURRENCY_LIMIT = 4
extraction_semaphore = asyncio.Semaphore(EXTRACTION_CONCURRENCY_LIMIT)

app = FastAPI(
    title="Lumina Extraction Service",
    description="A microservice for analyzing documents and extracting structured data.",
    version="1.0.0",
)

job_manager = JobStatusManager()

# ============================================================================
# Helper & Utility Functions
# ============================================================================

def _create_pydantic_model_from_code(model_code: str, model_name: str) -> Type[BaseModel]:
    """
    Dynamically executes Python code to create a Pydantic model.
    Includes robust error handling for missing imports.

    Args:
        model_code: The string containing the Python code for the Pydantic model.
        model_name: The expected class name of the model in the code.

    Returns:
        The dynamically created Pydantic model class.

    Raises:
        HTTPException: If the model cannot be created.
    """
    # Define a safe execution scope with common imports
    execution_scope = {
        "pydantic": pydantic,
        "BaseModel": pydantic.BaseModel,
        "Field": pydantic.Field,
        "Optional": Optional,
        "List": List,
        "Dict": Dict,
        "Any": Any,
        "Literal": pydantic.Field, # Common error to forget typing.Literal
        "field_validator": pydantic.field_validator
        # Add other common imports as needed
    }

    try:
        exec(model_code, execution_scope)
        return execution_scope[model_name]
    except NameError as e:
        logger.warning(f"NameError during initial model creation: {e}")
        match = re.search(r"name '(\w+)' is not defined", str(e))
        if not match:
            raise HTTPException(status_code=500, detail=f"Failed to parse NameError: {e}")

        missing_name = match.group(1)
        logger.info(f"Attempting to auto-import missing name: {missing_name}")

        # Try to find the missing name in pydantic or typing
        if hasattr(pydantic, missing_name):
            execution_scope[missing_name] = getattr(pydantic, missing_name)
            logger.info(f"Auto-imported '{missing_name}' from pydantic.")
        elif hasattr(__import__('typing'), missing_name):
            execution_scope[missing_name] = getattr(__import__('typing'), missing_name)
            logger.info(f"Auto-imported '{missing_name}' from typing.")
        else:
            raise HTTPException(status_code=500, detail=f"Pydantic model code failed: Missing import '{missing_name}' could not be found.")

        # Retry execution with the new scope
        try:
            exec(model_code, execution_scope)
            return execution_scope[model_name]
        except Exception as retry_e:
            raise HTTPException(status_code=500, detail=f"Model creation failed after auto-import: {retry_e}")
    except Exception as e:
        logger.error(f"Failed to execute model code: {model_code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create Pydantic model: {e}")
    

## for dynamic extraction
def _build_dynamic_model_code(
    field_name: str,
    field_description: str,
    field_type: str,
):
    """
    Builds a Pydantic model that expects a list of (value, record_id) pairs.
    """
    # NOTE: field_name is already the "safe_field_name"
    model_name_inner = f"DynamicField_{field_name.title()}"
    model_name_outer = f"DynamicFieldList_{field_name.title()}"

    py_type = {
        "string": "str",
        "number": "float",
        "integer": "int",
        "boolean": "bool",
        "list": "List[str]",
    }.get(field_type, "str")

    model_code = f"""
from pydantic import BaseModel, Field
from typing import List, Optional

class {model_name_inner}(BaseModel):
    value: Optional[{py_type}] = Field(
        default=None,
        description="{field_description}"
    )
    record_id: str = Field(
        description="The unique identifier for the record this value belongs to, e.g., 'record_123'."
    )

class {model_name_outer}(BaseModel):
    extracted_data: List[{model_name_inner}] = Field(
        description="A list of all the extracted data points."
    )
"""
    # We return the name of the OUTER model
    return model_name_outer, model_code


def _build_extraction_prompt(
    field_name: str,
    field_description: str,
    field_type: str,
    examples: Optional[List[str]] = None
) -> str:
    examples_text = f"\n\nExamples: {', '.join(examples)}" if examples else ""
    return (
        "Extract the following field from the document:\n\n"
        f"Field: {field_name}\n"
        f"Description: {field_description}\n"
        f"Type: {field_type}{examples_text}\n\n"
        "If the information is not found in the document, return None.\n"
    )


def _exec_dynamic_model_code(model_name: str, model_code: str):
    """
    Execute dynamic Pydantic code in a controlled scope and return the model class.
    Handles the common 'name ... is not defined' case for pydantic v2 decorators.
    """
    scope: Dict[str, Any] = {
        "BaseModel": pydantic.BaseModel,
        "Field": pydantic.Field,
        "Optional": Optional,
        "List": List,
        "Dict": Dict,
        "Any": Any,
        "Literal": Literal,
        # v2 extras
        "field_validator": getattr(pydantic, "field_validator", None),
        "model_validator": getattr(pydantic, "model_validator", None),
        "computed_field": getattr(pydantic, "computed_field", None),
        # v1 compat
        "validator": getattr(pydantic, "validator", None),
        "ValidationError": pydantic.ValidationError,
    }

    try:
        exec(model_code, scope)
        return scope[model_name]
    except NameError as e:
        # try to auto-import missing name
        missing = _parse_missing_name(str(e))
        if not missing:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create extraction model: {str(e)}",
            )

        # try to plug from pydantic or typing
        for module in (pydantic, __import__("typing")):
            if hasattr(module, missing):
                scope[missing] = getattr(module, missing)
                break

        # retry
        try:
            exec(model_code, scope)
            return scope[model_name]
        except Exception as e2:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to create extraction model even after importing {missing}: {e2}"
                ),
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create extraction model: {str(e)}",
        )


def _parse_missing_name(msg: str) -> Optional[str]:
    """
    parse "name 'field_validator' is not defined"
    """
    m = re.search(r"name '(\w+)' is not defined", msg)
    return m.group(1) if m else None
## end of dynamic extraction
    
# ============================================================================
# Core Logic for Background Tasks
# ============================================================================

async def generate_schema_with_agents(intention: str, recommendations: str) -> Dict[str, Any]:
    """
    Generate schema and Pydantic model using the agent pipeline.
    Steps:
    1. Generate schema recommendations (Agent 1)
    2. Generate extraction prompt (Agent 2)
    3. Generate Pydantic model code (Agent 3)
    """
    try:       
        if not recommendations:
            # Step 1: Generate schema recommendations
            print(f"[Agent 1] Generating schema for: {intention}")
            schema_result = await run_agent_gracefully(schema_agent, intention)
            recommendations = json.loads(schema_result.final_output.model_dump_json())

        # Step 2: Generate Pydantic model
        print("STEP 2: Creating Pydantic Model Dynamically")
        fields_to_include = json.dumps(recommendations['recommended_schema'], indent=2)
        print(f"Fields to include in Pydantic model: {fields_to_include}")
        print(f"[Agent 2] Generating Pydantic model...")
        code_result = await run_agent_gracefully(
            pydantic_code_agent,
            f"Task: {intention}\nFields: {fields_to_include}. Generate the Pydantic model accordingly without any limits or pattern for STRING fields unless explicitly required."
        )

        # Parse the code result with robust error handling
        try:
            # First, check if final_output is already a dict
            if isinstance(code_result.final_output, dict):
                code_dict = code_result.final_output
                print("✅ Code result is already a dictionary")
            # If it's a string, try parsing it
            elif isinstance(code_result.final_output, str):
                print(f"📝 Code result is a string, attempting to parse...")
                print(f"First 200 chars: {code_result.final_output[:200]}")

                # Try JSON parsing first (more robust)
                try:
                    code_dict = json.loads(code_result.final_output)
                    print("✅ Parsed as JSON successfully")
                except json.JSONDecodeError:
                    # Fall back to ast.literal_eval
                    try:
                        code_dict = ast.literal_eval(code_result.final_output)
                        print("✅ Parsed with ast.literal_eval successfully")
                    except (SyntaxError, ValueError) as e:
                        print(f"❌ Failed to parse with ast.literal_eval: {e}")
                        raise ValueError(f"Could not parse code result: {e}")
            else:
                # Unexpected type - try to convert to dict
                print(f"⚠️ Unexpected type: {type(code_result.final_output)}")
                print(f"Content: {code_result.final_output}")
                # Try to access as an object with attributes
                if hasattr(code_result.final_output, 'model_dump'):
                    code_dict = code_result.final_output.model_dump()
                    print("✅ Extracted dict using model_dump()")
                elif hasattr(code_result.final_output, '__dict__'):
                    code_dict = code_result.final_output.__dict__
                    print("✅ Extracted dict using __dict__")
                else:
                    raise ValueError(f"Unsupported final_output type: {type(code_result.final_output)}")

            pydantic_model_code = PydanticModelCode(**code_dict)
            print(f"✅ Created PydanticModelCode: {pydantic_model_code.model_name}")

        except Exception as e:
            print(f"❌ Error parsing code result: {e}")
            print(f"Raw final_output: {code_result.final_output}")
            print(f"Type: {type(code_result.final_output)}")
            raise

        # Step 3: Generate extraction prompt
        print(f"[Agent 3] Generating extraction prompt...")
        prompt_result = await run_agent_gracefully(
            extraction_prompt_agent,
            f"Task: {intention}\nFields: {fields_to_include}"
        )
       

        # Store schema for later use
        schema = {
            "model_name": pydantic_model_code.model_name,
            "model_code": pydantic_model_code.model_code,
            "extraction_prompt": prompt_result.final_output.prompt_text,
            "recommendations": recommendations
        }

        return {
            "success": True,
            "schema": schema
        }

    except MaxRetriesExceededError as e:
        print(f"Agent pipeline failed after retries: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        print(f"Error in schema generation: {e}")
        return {
            "success": False,
            "error": str(e)
        }
        
async def _process_file_with_semaphore(
    filepath: str, 
    model: type, 
    prompt: str,
    filename: str # Pass filename for logging
) -> dict:
    """
    Wraps the main file processing pipeline with a semaphore to
    control concurrency.
    """
    # This async with block is the "bouncer"
    # It will wait here if 4 tasks are already running
    async with extraction_semaphore:
        logger.info(f"Starting extraction for {filename} (semaphore slot acquired)...")
        try:
            # Once a slot is free, we run the *actual* work
            result = await process_file_pipeline(filepath, model, prompt)
            logger.info(f"Finished extraction for {filename} (semaphore slot released).")
            return result
        except Exception as e:
            logger.error(f"Pipeline failed for {filename} (semaphore slot released): {e}", exc_info=True)
            # Re-raise the exception so asyncio.gather can catch it
            raise e

async def do_extraction_work(session_id: int, job_id: str, intention: str):
    """
    The main background task for a full data extraction job.
    This function contains the complete, long-running extraction pipeline.
    """
    db: AsyncSession = None
    try:
        # Get a database session for this task
        db_session_generator = get_async_db()
        db = await anext(db_session_generator)

        await job_manager.update_status(job_id, "PROCESSING", "Fetching session and file data...")
        
        # 1. Fetch files and session from DB
        files_query = select(models.UploadedFile).where(models.UploadedFile.session_id == session_id)
        session_query = select(models.Session).where(models.Session.id == session_id)
        
        files_result = await db.execute(files_query)
        session_result = await db.execute(session_query)
        
        uploaded_files = files_result.scalars().all()
        session = session_result.scalar_one()

        if not uploaded_files:
            raise ValueError("No files found for this session.")
        
        # 2. Generate Schema
        await job_manager.update_status(job_id, "PROCESSING", "Generating extraction schema...")
        
        logger.info("SESSION RESULTS %s", session)
        
        use_analyzed_schema = session.analysis_results and session.analysis_results.get("recommendation")
        recommendation = session.analysis_results["recommendation"] if use_analyzed_schema else None
        
        schema_result = await generate_schema_with_agents(intention, recommendation)
        if not schema_result["success"]:
            raise Exception(f"Schema generation failed: {schema_result.get('error')}")

        session.schema_details = schema_result["schema"]
        flag_modified(session, "schema_details")
        await db.commit()

        # 3. Create Pydantic Model from generated code
        await job_manager.update_status(job_id, "PROCESSING", "Creating Pydantic model...")
        ExtractionModel = _create_pydantic_model_from_code(
            model_code=session.schema_details['model_code'],
            model_name=session.schema_details['model_name']
        )
        logger.info(f"Successfully created Pydantic model '{ExtractionModel.__name__}'")

        # 4. Extract data from all files in parallel
        await job_manager.update_status(job_id, "PROCESSING", f"Extracting data from {len(uploaded_files)} {'documents' if len(uploaded_files) > 1 else 'document'}...")

        tasks = []
        for file in uploaded_files:
            task = asyncio.create_task(
                _process_file_with_semaphore(
                    file.filepath,
                    ExtractionModel,
                    session.schema_details['extraction_prompt'],
                    file.filename # Pass for logging
                )
            )
            # Pair the task with the filename
            tasks.append((file.filename, task))
        extraction_results = await asyncio.gather(
            *[t for _, t in tasks], 
            return_exceptions=True
        )

        # 5. Process and Save Results
        all_extractions, extraction_errors = [], []
        for i, result in enumerate(extraction_results):
            filename = tasks[i][0] # Get the filename associated with this result
            
            if isinstance(result, Exception):
                logger.error(f"Extraction pipeline failed for {filename}: {result}")
                extraction_errors.append({"filename": filename, "error": str(result)})
                continue

            if result["error"]:
                logger.warning(f"Extraction error for {filename}: {result['error']}")
                extraction_errors.append({"filename": filename, "error": result["error"]})

            # Add the _source_document field to every record
            for record_data in result["results"]:
                record_data["_source_document"] = filename # <--- THIS IS THE FIX
                all_extractions.append(record_data)
        
        logger.info(f"Extraction complete. Total records: {len(all_extractions)}. Errors: {len(extraction_errors)}.")
       
        for record_data in all_extractions:
            db.add(models.ExtractedRecord(session_id=session_id, data=record_data))
        await db.commit()

        # 6. Finalize Job
        message = f"Extraction successful with {len(all_extractions)} {'records' if len(all_extractions) > 1 else 'record'}."
        if extraction_errors:
            message += f" ({len(extraction_errors)} files had errors)."
        
        final_result = ExtractionResponse(
            success=True,
            message=message,
            records=all_extractions,
            total_records=len(all_extractions),
            errors=extraction_errors or None
        )
        await job_manager.update_status(job_id, "COMPLETED", message, result=final_result.model_dump())

    except Exception as e:
        logger.error(f"Extraction job {job_id} failed", exc_info=True)
        await job_manager.update_status(job_id, "FAILED", str(e))
    finally:
        if db:
            await db.close()

async def do_dynamic_extraction_work(
    session_id: int,
    job_id: str,
    field_name: str,
    field_description: str,
    field_type: str,
    examples: Optional[List[str]],
):
    """
    Dynamic schema expansion:
    - user/LLM asks for a new field → we build a 1-field Pydantic model
    - we re-run an extraction pipeline on the original uploaded docs
    - we write the extracted field back into existing ExtractedRecord.data JSON
    - we return sample values + errors so the UI can update
    """
    # santize field name to be a valid python identifier
    safe_field_name = field_name.strip().replace(" ", "_").replace("-", "_")
    logger.info(f"Dynamic column job started. Sanitized name: '{safe_field_name}'")
    
    db: AsyncSession = None
    try:
        # Get a database session for this task
        db_session_generator = get_async_db()
        db = await anext(db_session_generator)
        
        await job_manager.update_status(job_id, "PROCESSING", "Fetching existing records and files...")
        
        # 1. Fetch all necessary data from the database
        records_query = select(models.ExtractedRecord).where(models.ExtractedRecord.session_id == session_id)
        files_query = select(models.UploadedFile).where(models.UploadedFile.session_id == session_id)
        session = await db.get(models.Session, session_id)
        
        existing_records = (await db.execute(records_query)).scalars().all()
        uploaded_files = (await db.execute(files_query)).scalars().all()

        if not existing_records or not uploaded_files or not session:
            raise ValueError("No existing records or source files found for this session.")
        
        # Create a mapping from filename to record for easy updating later
        records_by_file = {}
        logger.info(f"--- BUILDING records_by_file MAP FOR {len(existing_records)} RECORDS ---")
        for record in existing_records:
            source_doc = record.data.get("_source_document")
            if not source_doc:
                logger.warning(f"Record {record.id} missing _source_document field.")
                continue
            logger.info(f"Record {record.id} maps to source: '{source_doc}'")
            if source_doc not in records_by_file:
                records_by_file[source_doc] = []
            records_by_file[source_doc].append(record)
        logger.info(f"--- MAP CONTENTS: {records_by_file} ---")
        
        logger.info(f"Found {len(existing_records)} records and {len(uploaded_files)} files.")

        # 2. Generate and create the Pydantic model for the single new field
        await job_manager.update_status(job_id, "PROCESSING", f"Generating schema for new field '{field_name}'...")
        
        # get the query from session intention
        ## TODO: implement a method to get the column the user is doing the query based on and 
        # make sure we are also passing that column and example, and its type and description
        # to build the extraction code 
        model_name, model_code = _build_dynamic_model_code(
        field_name=field_name,
        field_description=field_description,
        field_type=field_type,
        )
        
        extraction_prompt = _build_extraction_prompt(
            field_name=field_name,
            field_description=field_description,
            field_type=field_type,
            examples=examples,
        )

        ExtractionModel = _exec_dynamic_model_code(model_name, model_code)
        
        # 3. Extract the new field from all documents in parallel
        await job_manager.update_status(job_id, "PROCESSING", f"Extracting '{field_name}' from {len(uploaded_files)} documents...")
        
        
        tasks: List[tuple[str, asyncio.Task, List[models.ExtractedRecord]]] = []
        for file_record in uploaded_files:
            records_for_this_file = records_by_file.get(file_record.filename, [])
            # --- ADD THIS LOG ---
            if not records_for_this_file:
                logger.warning(f"Skipping task for {file_record.filename}: No records mapped to this file.")
                continue
            # --- END LOG ---

            logger.info(f"Creating task for {file_record.filename} with {len(records_for_this_file)} records.")

            # --- START NEW PROMPT LOGIC ---
            
            # 1. Build the "Record Context Map"
            record_context_map = []
            for record in records_for_this_file:
                # Create a unique, simple string ID
                record_id_str = f"record_{record.id}"
                
                # Create a text snippet of the record's existing data
                record_snippet = "\n".join(
                    f"  - {key}: {str(value)[:100]}..." if isinstance(value, str) and len(str(value)) > 100 else f"  - {key}: {value}" 
                    for key, value in record.data.items()
                )
                record_context_map.append(f"ID: {record_id_str}\n{record_snippet}")
            
            context_string = "\n---\n".join(record_context_map)
            
            # Create a prompt specific to this file, telling the agent how many items to find
            file_specific_prompt = f"""
            {extraction_prompt}

            ---
            IMPORTANT INSTRUCTIONS:
            Here are the {len(records_for_this_file)} records from '{file_record.filename}'.
            Your priority should be to return exactly {len(records_for_this_file)} value(s) for the field '{safe_field_name}'.
            Examples of such cases is a resume with multiple work experience entries where the user asks for "project names" or "duration of that project".
            There are cases where you don't need to return values for every record in that document.
            Examples include when several different fields were extracted from the same document, but they are not related.
            For instance, when user asks for professional experience information such as title and company, maybe only 2 records exists for that. 
            And for the other records, correspond to a different section of the document like education or publication title where for these fields the first two records are empty.
            In such cases, return null for the records that don't have relevant information.
            
            
            For those records that you do find value, you MUST return a list of objects. Each object must contain:
            1.  `value`: The value you found (or `null` if not found).
            2.  `record_id`: The matching ID for that record (e.g., "record_123").
            ---
            RECORDS:
            {context_string}
            """
            
            task = asyncio.create_task(
            process_file_pipeline(
                file_record.filepath,
                ExtractionModel, # This is now the *outer* list model
                file_specific_prompt
            )
        )
            # We now also pass the list of records, so we can build a map later
            tasks.append((file_record.filename, task, records_for_this_file))
        logger.info(f">> Task list is {tasks}")
        # list only for task objectives
        extraction_tasks_to_run = [task_tuple[1] for task_tuple in tasks]    
        logger.info(f">> Extraction tasks to run: {extraction_tasks_to_run}")
        extraction_results = await asyncio.gather(
            *extraction_tasks_to_run, 
            return_exceptions=True
        )

        # 4. Process results and map them to existing records
        all_new_values = []
        extraction_errors = []
        records_updated_count = 0

        # --- START NEW MAPPING LOGIC ---
        # First, create a master dictionary of all records by their string ID
        all_records_by_id = {}
        for file, _, records_in_file in tasks:
            for record in records_in_file:
                all_records_by_id[f"record_{record.id}"] = record
        # --- END NEW MAPPING LOGIC ---
        logger.warning(f"EXTRACTION RESULTS {extraction_results}")
        for idx, result in enumerate(extraction_results):
            filename = tasks[idx][0]
            record_for_this_file = tasks[idx][2]
            # --- ADD THIS LOGGING ---
            logger.info(f"--- RAW AGENT RESULT FOR {filename} ---")
            logger.info(result)
            # --- END ADD ---
            if isinstance(result, Exception):
                logger.error(f"Dynamic extraction failed for {filename}: {str(result)}")
                extraction_errors.append({"filename": filename, "error": str(result)})
                continue
            
            if result.get("error"):
                logger.warning(f"Extraction error for {filename}: {result['error']}")
                extraction_errors.append({"filename": filename, "error": result["error"]})
                continue

            try:
                # The agent returns {'results': [ { 'extracted_data': [ {value: V, record_id: ID}, ... ] } ]}
                parsed_data_list = result.get("results", [{}])[0].get("extracted_data", [])
                
                # --- ADD THIS CHECK ---
                if not parsed_data_list:
                    logger.warning(f"Agent returned no data for {filename}. Parsed list is empty.")
                    extraction_errors.append({"filename": filename, "error": "Agent returned no data"})
                    continue
                # --- END ADD ---
                
                if not parsed_data_list:
                    logger.warning(f"Agent returned no data for {filename}.")
                    continue

                # Loop through the (value, record_id) pairs
               if len(records_for_this_file) == 1:
                    record = records_for_this_file[0]
                    values_list = []
                    for item in parsed_data_list:
                        value = item.get("value")
                        if value is not None:
                            if isinstance(value, list):
                                values_list.extend(value)
                            else:
                                values_list.append(value)
                    
                    # Store based on count
                    if len(values_list) == 1:
                        record.data[safe_field_name] = values_list[0]  # ← Single string
                    else:
                        record.data[safe_field_name] = values_list      # ← Array
                
                    
                    flag_modified(record, "data")
                    records_updated_count += 1
                    all_new_values.extend(values_list)
                    logger.info(f"Stored {len(values_list)} value(s) in single record for {filename}")  # ← Change log message
                else:
                    # Multiple records → map value to each record by record_id
                    for item in parsed_data_list:
                        value = item.get("value")
                        record_id = item.get("record_id")
                        
                        if not record_id:
                            logger.warning(f"Agent returned a value ({value}) without a record_id.")
                            continue
                        
                        # Find the record in our master dictionary
                        record_to_update = all_records_by_id.get(record_id)
                        
                        if record_to_update:
                            record_to_update.data[safe_field_name] = value
                            flag_modified(record_to_update, "data")
                            records_updated_count += 1
                            all_new_values.append(value)
                        else:
                            logger.error(f"Agent returned data for an unknown {record_id}.")

            except Exception as e:
                logger.error(f"Failed to parse agent response for {filename}: {e}")
                extraction_errors.append({"filename": filename, "error": f"Failed to parse agent response: {e}"})
                
        logger.info(f"Dynamic extraction complete. Explicitly mapped and updated {records_updated_count} records.")
        # 5. Update records in the database
        await job_manager.update_status(job_id, "PROCESSING", f"Updating {records_updated_count} records in the database...")
        new_field_schema = {
            "name": safe_field_name,
            "type": field_type,
            "description": field_description
        }
        if 'fields' not in session.schema_details:
             session.schema_details['fields'] = []
             
        session.schema_details['fields'].append(new_field_schema)
        flag_modified(session, "schema_details")
        
        await db.commit() # Commits all record and session changes

        # 6. Finalize Job
        message = f"Successfully added '{field_name}' to {records_updated_count} records."
        sample_values = [v for v in all_new_values if v is not None][:3]
        
        final_result = DynamicColumnResponse(
            success=True,
            message=message,
            field_name=safe_field_name,
            records_updated=records_updated_count,
            sample_values=sample_values,
            new_field=new_field_schema,
            new_records= None
        )
        await job_manager.update_status(job_id, "COMPLETED", message, result=final_result.model_dump())

    except Exception as e:
        logger.error(f"Dynamic column job {job_id} failed", exc_info=True)
        error_message = str(e.detail) if isinstance(e, HTTPException) else str(e)
        await job_manager.update_status(job_id, "FAILED", error_message)
        if db:
            await db.rollback()
        
    finally:
        if db:
            await db.close()

async def do_analysis_work(session_id: int, job_id: str):
    """
    Background task to perform document analysis.
    This function creates its own DB session.
    """
    logger.info(f"Background analysis for job {job_id} (Session {session_id}) started.")
    
    db: AsyncSession = None
    try:
        # Get a database session for this task
        db_session_generator = get_async_db()
        db = await anext(db_session_generator)

        # Fetch files for the session
        files_query = select(models.UploadedFile).where(models.UploadedFile.session_id == session_id)
        files_result = await db.execute(files_query)
        uploaded_files = files_result.scalars().all()

        if not uploaded_files:
            logger.warning(f"No files found for job {job_id}. Marking as FAILED.")
            await job_manager.update_status(job_id, "FAILED", "No files found for this session.")
            return

        # Run analysis pipeline
        await job_manager.update_status(job_id, "PROCESSING", f"Found {len(uploaded_files)} files. Analyzing and creating extraction schema...")
        analysis_result = await analyze_documents_pipeline([f.filepath for f in uploaded_files])
        if not analysis_result["success"]:
            error_msg = analysis_result.get("error", "Unknown error during analysis.")
            logger.error(f"Analysis failed for job {job_id}: {error_msg}")
            await job_manager.update_status(job_id, "FAILED", f"Analysis failed: {error_msg}")
            return

        # Store analysis results in the session
        await job_manager.update_status(job_id, "PROCESSING", "Analysis complete. Storing results...")
        session_query = select(models.Session).where(models.Session.id == session_id)
        session = (await db.execute(session_query)).scalar_one()
        session.analysis_results = analysis_result
        flag_modified(session, "analysis_results")
        await db.commit()

        # Finalize job
        logger.info(f"Successfully analyzed documents for job {job_id}.")
        await job_manager.update_status(job_id, "COMPLETED", "Analysis completed successfully.", result=analysis_result)
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed", exc_info=True)
        await job_manager.update_status(job_id, "FAILED", str(e))
        if db:
            await db.rollback()
    finally:
        if db:
            await db.close()
            
# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Lumina Extraction Service"}


@app.post("/update-schema")
async def update_schema_endpoint(req: UpdateSchemaRequest, db: AsyncSession = Depends(get_async_db)):
    """Updates the recommended schema with user edits."""
    session_query = select(models.Session).where(models.Session.id == req.session_id)
    session = (await db.execute(session_query)).scalar_one_or_none()
    if not session or not session.analysis_results:
        raise HTTPException(status_code=404, detail="Analysis must be run before updating schema.")
    
    session.analysis_results["recommendation"]["recommended_intention"] = req.intention
    session.analysis_results["recommendation"]["recommended_schema"] = req.fields
    flag_modified(session, "analysis_results")
    await db.commit()
    
    return {"success": True, "message": "Schema updated successfully."}

@app.post("/analyze")
async def analyze_documents_endpoint(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Kicks off a document analysis job in the background.
    """
    
    
    await job_manager.create_job(req.job_id, service="analysis")
    background_tasks.add_task(do_analysis_work, req.session_id, req.job_id)

    return {"job_id": req.job_id, "message": "Analysis job initiated."}

            
@app.post("/extract", status_code=202)
async def start_extraction_endpoint(req: ExtractionJobRequest, background_tasks: BackgroundTasks):
    """
    Kicks off a new data extraction job in the background.
    """
    await job_manager.create_job(req.job_id, service="extraction")
    background_tasks.add_task(do_extraction_work, req.session_id, req.job_id, req.intention)
    return {"job_id": req.job_id, "message": "Extraction job has been started."}

@app.post("/add-dynamic-column", status_code=202)
async def add_dynamic_column_endpoint(req: DynamicColumnJobRequest, background_tasks: BackgroundTasks):
    """
    Kicks off a job to extract a single new field and add it to existing records.
    """
    await job_manager.create_job(req.job_id, service="extraction-dynamic-column")
    
    background_tasks.add_task(
        do_dynamic_extraction_work,
        session_id=req.session_id,
        job_id=req.job_id,
        field_name=req.field_name,
        field_description=req.field_description,
        field_type=req.field_type,
        examples=req.examples
    )
    
    return {"job_id": req.job_id, "message": "Dynamic column extraction job has been started."}