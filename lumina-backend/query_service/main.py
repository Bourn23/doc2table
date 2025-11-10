import logging
import asyncio
import os
import time
from pathlib import Path
from typing import Dict, Optional, List, Any, Literal
import re
import pydantic

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
import httpx
import uuid

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

# Import shared components
import shared.models as models
from shared.database import get_async_db, settings
from shared.job_manager import JobStatusManager
from lumina_agents.rag_agent import RAGSystem
from shared.api_types import (
    IndexJobRequest, IndexResponse, QueryRequest, QueryResponse,
    GraphGenerationRequest, GraphGenerationResponse, NodeModel, RelationshipModel
)
from lumina_agents.query_agents import query_router_agent, synthesis_agent
from lumina_agents.extraction_agents import process_file_pipeline
from shared.utils import (
    create_text_chunks_from_data, create_column_chunks_from_data,
    run_agent_gracefully, export_to_csv
)

# Graph agent imports
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Import boto for S3 exports
from botocore.exceptions import ClientError
from shared.aws_client import session, S3_BUCKET_NAME
from shared.utils import export_to_s3

# ============================================================================
# Service Setup
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONCURRENCY_LIMIT = 3
rag_semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

app = FastAPI(
    title="Lumina Query Service",
    description="A microservice for indexing data, handling RAG queries, and generating knowledge graphs.",
    version="1.0.0",
)

job_manager = JobStatusManager()
INDEXES_DIR = Path("/data/indexes")
RAG_SYSTEMS_CACHE: Dict[str, RAGSystem] = {} # In-memory cache for loaded indexes

# Log startup information
logger.info(f"🚀 Query Service starting up")
logger.info(f"📁 INDEXES_DIR: {INDEXES_DIR}")
logger.info(f"📁 INDEXES_DIR exists: {INDEXES_DIR.exists()}")
if INDEXES_DIR.exists():
    sessions = [f.name for f in INDEXES_DIR.iterdir() if f.is_dir()]
    logger.info(f"📁 Available sessions: {sessions}")

# ============================================================================
# Neo4j & Graph Transformer Setup
# ============================================================================
NEO4J_URL = os.getenv("NEO4J_URL", "neo4j://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")
GRAPH_LLM_MODEL = os.getenv("GRAPH_LLM_MODEL", "nvidia/llama-3.1-nemotron-nano-8b-v1")

# graph = Neo4jGraph(url=NEO4J_URL, username=NEO4J_USER, password=NEO4J_PASS)
graph = None # for debugging

llm = ChatNVIDIA(model=GRAPH_LLM_MODEL)
graph_transformer = LLMGraphTransformer(llm=llm, ignore_tool_usage=True)

def cleanup_old_graphs():
    """Deletes graph nodes and relationships older than 1 hour."""
    try:
        one_hour_ago = int(time.time()) - 3600
        if graph is not None:
            graph.query("MATCH (n) WHERE n.created_at < $ts DETACH DELETE n", {"ts": one_hour_ago})
        logger.info("Cleaned up old graph data from Neo4j.")
    except Exception as e:
        logger.error(f"Failed to cleanup old graphs: {e}", exc_info=True)


# ============================================================================
# Helper & Utility Functions
# ============================================================================
def rag_to_query_response(pipeline_result: dict) -> dict:
    """
    Take the raw dict returned by RAGSystem.run_pipeline(...) and
    turn it into what our QueryResponse pydantic model expects.
    """
    answer = pipeline_result.get("answer", "")
    retrieved = pipeline_result.get("retrieved_results", []) or []
    reranked = pipeline_result.get("reranked_results", []) or []

    # 1. confidence
    # prefer rerank_score if available, else similarity_score, else 0.0
    if reranked and "rerank_score" in reranked[0]:
        confidence = float(reranked[0]["rerank_score"])
    elif retrieved and "similarity_score" in retrieved[0]:
        confidence = float(retrieved[0]["similarity_score"])
    else:
        confidence = 0.0

    # 2. sources: light version of the chunks
    sources = []
    for item in reranked or retrieved:
        sources.append(
            {
                "chunk_id": item.get("chunk_id"),
                "score": float(
                    item.get("rerank_score", item.get("similarity_score", 0.0))
                ),
                "text_preview": item.get("text_preview") or item.get("text", "")[:200],
            }
        )
    

    # 3. relevant_records: if you have table-like chunks, just return them all
    # later we can make this smarter
    relevant_records = []
    for item in reranked or retrieved:
        relevant_records.append(
            {
                "chunk_id": item.get("chunk_id"),
                "text": item.get("text"),
                "score": float(
                    item.get("rerank_score", item.get("similarity_score", 0.0))
                ),
            }
        )

    return {
        "answer": answer,
        "query": pipeline_result.get("query", ""),
        "confidence": confidence,
        "sources": sources,
        "relevant_records": relevant_records,
        "result_type": "rag",
    }
    
async def get_or_load_rag_system(session_id: int, index_name: str) -> RAGSystem:
    """
    Loads a RAG system from disk into a local cache if not already present.
    """
    cache_key = f"{session_id}_{index_name}"
    if cache_key in RAG_SYSTEMS_CACHE:
        logger.info(f"Found RAG system '{cache_key}' in cache.")
        return RAG_SYSTEMS_CACHE[cache_key]

    index_path = INDEXES_DIR / str(session_id) / index_name
    
    # Log what files we can see for debugging
    session_dir = INDEXES_DIR / str(session_id)
    if session_dir.exists():
        available_indexes = [f.name for f in session_dir.iterdir() if f.is_dir()]
        logger.info(f"Available indexes in session {session_id}: {available_indexes}")
    else:
        logger.warning(f"Session directory does not exist: {session_dir}")
        logger.info(f"INDEXES_DIR contents: {[f.name for f in INDEXES_DIR.iterdir()] if INDEXES_DIR.exists() else 'INDEXES_DIR does not exist'}")
    
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found for session {session_id}. Available: {available_indexes if session_dir.exists() else 'none'}")

    logger.info(f"Loading RAG system from '{index_path}' into cache...")
    rag_system = RAGSystem(
            embed_api_key=settings.NVIDIA_EMBED_API_KEY,
            rerank_api_key=settings.NVIDIA_RERANK_API_KEY,
            gemini_api_key=settings.GOOGLE_GEMINI_API_KEY
        )
    await asyncio.to_thread(rag_system.load_index, str(index_path))
    
    RAG_SYSTEMS_CACHE[cache_key] = rag_system
    return rag_system
# ============================================================================
# Core Logic for Background Tasks
# ============================================================================

async def do_indexing_work(session_id: int, job_id: str):
    """Background task to fetch data, create, and save RAG indexes."""
    db: AsyncSession = None
    try:
        db_session_generator = get_async_db()
        db = await anext(db_session_generator)
        
        await job_manager.update_status(job_id, "PROCESSING", "Fetching extracted records from database...")
        
        query = select(models.ExtractedRecord).where(models.ExtractedRecord.session_id == session_id)
        result = await db.execute(query)
        records = [r.data for r in result.scalars().all()]
        if not records:
            raise ValueError("No extracted records found in the database for this session.")

        # --- 1. Row-wise Indexing ---
        await job_manager.update_status(job_id, "PROCESSING", "Creating row-wise index...")
        row_chunks = create_text_chunks_from_data(records)
        row_wise_rag = RAGSystem(
            embed_api_key=settings.NVIDIA_EMBED_API_KEY,
            rerank_api_key=settings.NVIDIA_RERANK_API_KEY,
            gemini_api_key=settings.GOOGLE_GEMINI_API_KEY
        )
        per_chunk_meta = [{"row_index": i} for i in range(len(row_chunks))]
        await asyncio.to_thread(
            row_wise_rag.index_documents, 
            row_chunks,
            base_metadata={
                "session_id": session_id,
                "index_type": "row_wise",
            },
            per_chunk_metadata=per_chunk_meta,
        )
        
        row_wise_path = INDEXES_DIR / str(session_id) / "row_wise"
        row_wise_path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(row_wise_rag.save_index, str(row_wise_path))
        logger.info(f"Saved row-wise index to {row_wise_path}")

        # --- 2. Column-wise Indexing ---
        await job_manager.update_status(job_id, "PROCESSING", "Creating column-wise indexes...")
        columns_to_index = list(records[0].keys()) # Example: index all columns
        column_chunks_map = create_column_chunks_from_data(records, columns_to_index)

        for col_name, chunk_text in column_chunks_map.items():
            col_rag = RAGSystem(
                embed_api_key=settings.NVIDIA_EMBED_API_KEY,
                rerank_api_key=settings.NVIDIA_RERANK_API_KEY,
                gemini_api_key=settings.GOOGLE_GEMINI_API_KEY
            )
            await asyncio.to_thread(col_rag.index_documents, 
                                    [chunk_text],
                                    base_metadata={
                                        "session_id": session_id,
                                        "index_type": f"column_wise",
                                        "column_name": col_name
                                    },
                                    per_chunk_metadata=[{"column_name": col_name}]
                                )
            
            col_path = INDEXES_DIR / str(session_id) / f"column_{col_name}"
            await asyncio.to_thread(col_rag.save_index, str(col_path))
            logger.info(f"Saved column-wise index for '{col_name}' to {col_path}")
        
        message = f"Successfully created {1 + len(column_chunks_map)} indexes."
        await job_manager.update_status(job_id, "COMPLETED", message)

    except Exception as e:
        logger.error(f"Indexing job {job_id} failed", exc_info=True)
        # Mark as completed with warning instead of failed - extraction was successful
        await job_manager.update_status(
            job_id, 
            "COMPLETED_WITH_WARNING", 
            f"Data extraction succeeded, but RAG indexing failed: {str(e)}. You can view and export your data, but semantic search queries will not be available."
        )
    finally:
        if db:
            await db.close()

async def merge_column_query_results(
    column_results: List[Dict[str, Any]], 
    query: str,
    target_columns: List[str],
    num_results: int = 10 # --- FIX: Added num_results ---
) -> Dict[str, Any]:
    """
    Merge results from multiple column RAG queries into a single response.
    
    Args:
        column_results: List of dicts with 'column' and 'result' keys
        query: Original user query
        target_columns: List of column names that were queried
    
    Returns:
        Dict suitable for QueryResponse
    """
    # Collect all sources and contexts from each column
    all_sources = []
    all_contexts = []
    all_relevant_records = []
    
    for col_result in column_results:
        column_name = col_result["column"]
        result = col_result["result"]
        
        # Get retrieved and reranked results
        retrieved = result.get("retrieved_results", []) or []
        reranked = result.get("reranked_results", []) or []
        results_to_use = reranked if reranked else retrieved
        
        # Add column metadata to sources
        for item in results_to_use:
            all_sources.append({
                "chunk_id": item.get("chunk_id"),
                "column": column_name,  # Tag with column name
                "score": float(item.get("rerank_score", item.get("similarity_score", 0.0))),
                "text_preview": item.get("text_preview") or item.get("text", "")[:200],
            })
            
            # Collect contexts with column tags
            text = item.get("text", "")
            all_contexts.append(f"[From column '{column_name}']: {text}")
            
            # Collect relevant records
            all_relevant_records.append({
                "chunk_id": item.get("chunk_id"),
                "column": column_name,
                "text": text,
                "score": float(item.get("rerank_score", item.get("similarity_score", 0.0))),
            })
    
    # Sort sources by score (descending)
    all_sources.sort(key=lambda x: x["score"], reverse=True)
    all_relevant_records.sort(key=lambda x: x["score"], reverse=True)
    
    # Limit to top results
    top_sources = all_sources[:num_results]
    top_records = all_relevant_records[:num_results]

    # Get top contexts for synthesis
    top_contexts = all_contexts[:20]  # Use more contexts for synthesis
    
    # Synthesize answer from multiple columns   
    columns_list = ", ".join([f"'{col}'" for col in target_columns])
    context_text = "\n\n".join(top_contexts)
    SYNTHESIS_PROMPT = f"""You are answering a query about data from multiple columns: {columns_list}.

    Here is the relevant information from these columns:

    {context_text}

    User Query: {query}

    Please provide a comprehensive answer that synthesizes information from all the columns. 
    Make sure to integrate insights from different columns naturally.
    If information from different columns relates to each other, highlight those connections."""

    synthesized_answer = await run_agent_gracefully(synthesis_agent, SYNTHESIS_PROMPT)
    parsed_synthesis = synthesized_answer.final_output

    # Calculate combined confidence (average of top scores)
    if top_sources:
        confidence = sum(s["score"] for s in top_sources[:3]) / min(3, len(top_sources))
    else:
        confidence = 0.0
    
    return {
        "query": query,
        "answer": parsed_synthesis,
        "confidence": confidence,
        "sources": top_sources,
        "relevant_records": top_records,
        "result_type": "rag",
    }

def sanitize_field_name(field_name: str) -> str:
    """Sanitize field name to match the format used when saving indexes."""
    return field_name.strip().replace(" ", "_").replace("-", "_")

async def _query_single_column(
    session_id: int, 
    column_name: str, 
    query: str, 
    num_results: int
) -> Dict[str, Any] | None:
    """
    Async helper to query one RAG index.
    Returns None if a specific column query fails.
    """
    # Sanitize column name to match the format used when saving indexes
    safe_column_name = sanitize_field_name(column_name)
    index_name = f"column_{safe_column_name}"
    async with rag_semaphore:
        logger.info(f"Starting query for column: {column_name} (Semaphore acquired)")
        try:
            rag_system = await get_or_load_rag_system(session_id, index_name)
            
            # The code that hits the server is now inside the semaphore block
            pipeline_result = await asyncio.to_thread(
                rag_system.run_pipeline,
                query=query,
                rerank_top_k=num_results,
                skip_generation=True  # Skip generation for column queries since we will synthesize later
            )
            
            logger.info(f"Successfully queried column: {column_name} (Semaphore released)")
            return {"column": column_name, "result": pipeline_result}
        
        except Exception as e:
            logger.warning(f"Failed to query column {column_name}: {e}")
            return None # return None instead of crashing
    
    
# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Lumina Query Service"}

@app.post("/index", status_code=202)
async def start_indexing_endpoint(req: IndexJobRequest, background_tasks: BackgroundTasks):
    """Kicks off a new data indexing job in the background."""
    await job_manager.create_job(req.job_id, service="indexing")
    background_tasks.add_task(do_indexing_work, req.session_id, req.job_id)
    return {"job_id": req.job_id, "message": "Indexing job has been started."}

@app.post("/query", response_model=QueryResponse)
async def query_data_endpoint(req: QueryRequest, db: AsyncSession = Depends(get_async_db)):
    """Routes a user query to the appropriate handler (RAG or function call)."""
    try:
        session_query = select(models.Session).where(models.Session.id == req.session_id)
        session = (await db.execute(session_query)).scalar_one()
        
        # Try 'fields' first, fall back to recommended_schema
        old_schema_fields = session.schema_details.get('fields', []) 
        # schema_fields = None
        
        # if not schema_fields:
            # Fall back to recommended schema - it's already a list!
        recommended = session.schema_details.get('recommendations', {}).get('recommended_schema', [])
        new_schema_fields = recommended  # ← Don't call .get('fields') on it!
            # logger.info("Using recommended schema as fallback")
        
        # logger.info("Schema fields: %s", schema_fields)
        
        # Handle different field name formats (field_name vs name)
        columns = []
        for field in old_schema_fields:
            # Try 'name' first (used in dynamic extraction), fall back to 'field_name' (used in initial schema)
            col_name = field.get('name') or field.get('field_name')
            if col_name:
                columns.append(col_name)
        for field in new_schema_fields:
            col_name = field.get('name') or field.get('field_name')
            if col_name and col_name not in columns:
                columns.append(col_name)
        
        logger.info("Extracted column names: %s", columns)

        # Fetch data preview
        first_record_query = select(models.ExtractedRecord).where(
            models.ExtractedRecord.session_id == req.session_id
        ).limit(1)
        first_record_result = await db.execute(first_record_query)
        first_record = first_record_result.scalar_one_or_none()

        data_preview = "No data available in the first record."
        if first_record and first_record.data:
            preview_items = []
            for col in columns:
                val = first_record.data.get(col)
                if val is not None:
                    val_str = str(val)
                    if len(val_str) > 70:
                        val_str = val_str[:70] + "..."
                    preview_items.append(f"  - {col}: {val_str}")
            data_preview = "\n".join(preview_items)
        
        logger.info("Agent is seeing these columns: %s", columns)
        router_input = f"""User Query: {req.query}
        
        Existing columns: {', '.join(columns)}

Data Preview (from first record) -- use this to understand data types and content to decide if you need to do dynamic extraction or RAG querying:
{data_preview}
"""
        router_result = await run_agent_gracefully(query_router_agent, router_input)
        intent = router_result.final_output

        logger.info(f"Query routed to intent: {intent.intent_type} || BECAUSE {intent.reasoning}")
        
        if intent.intent_type == "function":
            # Logic for function calls like exporting data
            records_query = select(models.ExtractedRecord).where(models.ExtractedRecord.session_id == req.session_id)
            records = [r.data for r in (await db.execute(records_query)).scalars().all()]
            export_result = await export_to_csv(records=records, filename=f"session_{req.session_id}_export")
            
            return QueryResponse(
                success=True, 
                query = req.query,
                answer=export_result["message"], 
                confidence=1.0,
                result_type="function", 
                function_result=export_result)
        
        
            #         export_dict = await export_to_s3(records=records, filename=f"session_{req.session_id}_export")
            
            # fn_result = FunctionResult(
            #     success=export_dict["success"],
            #     message=export_dict["message"],
            #     s3_key=export_dict.get("s3_key"),  # Use .get() for safety
            #     record_count=export_dict.get("record_count")
            # )
            
            # return QueryResponse(
            #     success=True, 
            #     query = req.query,
            #     answer=fn_result.message, 
            #     confidence=1.0,
            #     result_type="function", 
            #     function_result=fn_result)
        
        if "dynamic_extraction" in intent.intent_type:
            new_field_name = intent.new_field.name or "new_field"
            new_field_description = intent.new_field.description or "Dynamically extracted field"
            new_field_type = intent.new_field.type or "string"

            logger.info(
                "Dynamic extraction requested: %s (%s)",
                new_field_name,
                new_field_type
            )
            # 1. Get the URL for the extraction service
            extraction_service_url = os.getenv("EXTRACTION_SERVICE_URL", "http://extraction-service:8001")
            
            # 2. Create a new, unique job_id for this background task
            new_job_id = str(uuid.uuid4())

            # 3. Create the request payload for the extraction service
            # This matches the 'DynamicColumnJobRequest' your endpoint expects
            payload = {
                "job_id": new_job_id,
                "session_id": req.session_id, # From the original QueryRequest
                "field_name": new_field_name,
                "field_description": new_field_description,
                "field_type": new_field_type,
                "examples": None # The agent doesn't provide examples, but the API can
            }

            # 4. Make the async HTTP call to start the job
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{extraction_service_url}/add-dynamic-column",
                        json=payload,
                        timeout=10.0 # Starting a job should be fast
                    )
                    # Raise an error if the service didn't accept the job
                    response.raise_for_status() 
                
                except httpx.HTTPStatusError as e:
                    logger.error(f"Failed to start dynamic extraction job: {e.response.text}")
                    raise HTTPException(status_code=502, detail=f"Extraction service failed to start job: {e.response.json()}")
                except httpx.RequestError as e:
                    logger.error(f"Failed to connect to extraction service: {e}")
                    raise HTTPException(status_code=503, detail="Extraction service is unavailable.")

            # 5. Return a response telling the frontend a *new job* was started
            # The frontend can then use this new_job_id to start tracking
            # a new job on its WebSocket.
            return QueryResponse(
                success=True,
                query=req.query,
                answer=f"I am re-analyzing your data to add the field '{new_field_name}'. It won't take long",
                confidence=1.0,
                sources=[],
                relevant_records=[],
                result_type="function_job_start", # Use a special type for the UI
                function_result={
                    "success": True,
                    "message": "Dynamic column extraction job has been started.",
                    "new_job_id": new_job_id # This is the critical part
                }
            )
        
        if intent.intent_type == "rag_column_wise" and intent.target_columns:
            # multi-column analysis
            # either, query each column index separately and merge results
            # create a combined index for multiple columns
            # use a single index with column metadata
            
            tasks = []
            for column in intent.target_columns:
                tasks.append(
                    _query_single_column(
                        session_id=req.session_id,
                        column_name=column,
                        query=req.query,
                        num_results=req.num_results
                    )
                )
            
            # Gather all results concurrently
            all_column_results = await asyncio.gather(*tasks)
            
            # Filter out any that failed (returned None)
            successful_column_results = [res for res in all_column_results if res is not None]
            
            if not successful_column_results:
                raise HTTPException(
                    status_code=500, 
                    detail="No columns could be queried successfully"
                )
            
            merged_response = await merge_column_query_results(
                column_results=successful_column_results, 
                query=req.query, 
                target_columns=intent.target_columns,
                num_results=req.num_results # --- FIX: Pass num_results in
            )
            return QueryResponse(success=True, **merged_response)
            
        else:
            index_name = "row_wise"
            
            # check if there's a row_filters in the intent.row_filters
            if intent.row_filters:
                logger.info(f"Applying row filters to query: {intent.row_filters}")
                # Note: Actual filtering logic would depend on how RAGSystem supports it
                # For now, we just log it.
            
            try:
                rag_system = await get_or_load_rag_system(req.session_id, index_name)
                pipeline_result = await asyncio.to_thread(
                    rag_system.run_pipeline,
                    query=req.query,
                    rerank_top_k=req.num_results
                )
                return QueryResponse(success=True, **rag_to_query_response(pipeline_result))
            except HTTPException as e:
                if e.status_code == 404:
                    # Index not found - RAG is unavailable
                    return QueryResponse(
                        success=True,
                        query=req.query,
                        answer="I'm sorry, but semantic search is currently unavailable because the data indexing failed during extraction. However, your data was extracted successfully and you can view it in the table below. You can also use function calls like 'Export as CSV' which will work normally.",
                        confidence=0.0,
                        sources=[],
                        relevant_records=[],
                        result_type="rag"
                    )
                else:
                    raise

    except Exception as e:
        logger.error(f"Error during /query for session {req.session_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-graph", response_model=GraphGenerationResponse)
async def generate_graph_endpoint(req: GraphGenerationRequest):
    """Generates a knowledge graph from RAG results and stores it in Neo4j."""
    cleanup_old_graphs()
    if not req.relevant_records:
        raise HTTPException(status_code=400, detail="No relevant records provided.")

    try:
        combined_text = "\n\n---\n\n".join([r['text'] for r in req.relevant_records])
        documents = [Document(page_content=combined_text)]
        
        graph_docs = await graph_transformer.aconvert_to_graph_documents(documents)
        
        current_ts = int(time.time())
        for doc in graph_docs:
            for node in doc.nodes:
                node.properties["query_id"] = req.query_id
                node.properties["created_at"] = current_ts
            for rel in doc.relationships:
                rel.properties["query_id"] = req.query_id
                rel.properties["created_at"] = current_ts
        if graph is not None:
            await asyncio.to_thread(
                graph.add_graph_documents,
                graph_docs
            )

        return GraphGenerationResponse(
            success=True,
            message="Knowledge graph generated successfully.",
            nodes=[NodeModel(**node.dict()) for node in graph_docs[0].nodes],
            relationships=[RelationshipModel(**rel.dict()) for rel in graph_docs[0].relationships]
        )
    except Exception as e:
        logger.error(f"Error during /generate-graph for query {req.query_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate graph: {e}")

@app.get("/download/{filename}")
async def download_file_endpoint(filename: str):
    """
    Serves a file from the 'exports' directory.
    Note: In a production setup, this might be handled by the API Gateway or a dedicated static file server.
    """
    filepath = Path("/data/exports") / filename
    if not filepath.is_file():
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(status_code=410, detail="File not found.")
    
    return FileResponse(path=filepath, media_type='text/csv', filename=filename)