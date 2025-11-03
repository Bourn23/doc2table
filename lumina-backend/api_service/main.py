import logging
import uuid
import os
import httpx
import asyncio
from pathlib import Path

from fastapi import (
    FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket,
    WebSocketDisconnect, File, UploadFile, Form
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import shared components
import shared.models as models
from shared.database import get_async_db, engine
from shared.job_manager import JobStatusManager
from shared.api_types import (
    ExtractionJobRequest, IndexJobRequest, QueryRequest, AnalyzeRequest,
    UpdateSchemaRequest, InitiateUploadRequest, InitiateUploadResponse,
    GraphGenerationRequest
)

# ============================================================================
# Service Setup
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lumina API Service (Gateway)",
    description="The main user-facing API that orchestrates backend microservices.",
    version="1.0.0",
)

# CORS Middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3001", "http://localhost:5173"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_manager = JobStatusManager()

# URLs for the backend worker services
EXTRACTION_SERVICE_URL = os.getenv("EXTRACTION_SERVICE_URL", "http://extraction-service:8001")
QUERY_SERVICE_URL = os.getenv("QUERY_SERVICE_URL", "http://query-service:8002")


@app.on_event("startup")
async def on_startup():
    """Create database tables on startup if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Checks the health of the API service and its connection to workers."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            extraction_health = await client.get(f"{EXTRACTION_SERVICE_URL}/health")
            query_health = await client.get(f"{QUERY_SERVICE_URL}/health")
            
            return {
                "status": "healthy",
                "service": "Lumina API Gateway",
                "dependencies": {
                    "extraction_service": "healthy" if extraction_health.is_success else "unhealthy",
                    "query_service": "healthy" if query_health.is_success else "unhealthy"
                }
            }
        except httpx.ConnectError as e:
            raise HTTPException(status_code=503, detail=f"A worker service is unavailable: {e}")


@app.post("/uploads/initiate", response_model=InitiateUploadResponse)
async def initiate_upload_endpoint(req: InitiateUploadRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Phase 1: Creates a new session and placeholder records for all expected files.
    This is a fast, synchronous call that returns a session_id immediately.
    """
    if not req.filenames:
        raise HTTPException(status_code=400, detail="No filenames provided.")

    try:
        # Create a new session for this upload batch
        new_session = models.Session()
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)

        # Create the session-specific directory on the shared volume
        session_dir = Path("/data/uploaded_files") / str(new_session.id)
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create placeholder records in the database for each file
        for filename in req.filenames:
            file_record = models.UploadedFile(
                session_id=new_session.id,
                filename=filename,
                status="PENDING" # Filepath and size are initially null
            )
            db.add(file_record)
        
        await db.commit()
        
        logger.info(f"Initiated upload session {new_session.id} for {len(req.filenames)} files.")
        return InitiateUploadResponse(success=True, session_id=new_session.id)
    
    except Exception as e:
        await db.rollback()
        logger.error("Failed to initiate upload session", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create upload session.")


@app.post("/uploads/file")
async def upload_file_endpoint(
    session_id: int = Form(...), 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_async_db)
):
    """
    Phase 2: Uploads a single file and updates its record in the database.
    The frontend calls this endpoint repeatedly for each file.
    """
    try:
        # Find the placeholder record for this file
        query = select(models.UploadedFile).where(
            models.UploadedFile.session_id == session_id,
            models.UploadedFile.filename == file.filename,
            models.UploadedFile.status == "PENDING"
        )
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise HTTPException(status_code=404, detail=f"No pending upload record found for '{file.filename}' in session {session_id}.")

        # Save the file to the shared volume
        file_path = Path("/data/uploaded_files") / str(session_id) / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)

        # Update the database record with the final details
        file_record.filepath = str(file_path)
        file_record.filesize = len(content)
        file_record.status = "UPLOADED"
        await db.commit()
        
        logger.info(f"Successfully uploaded '{file.filename}' for session {session_id}.")
        return {"success": True, "filename": file.filename, "status": "UPLOADED"}

    except Exception as e:
        await db.rollback()
        logger.error(f"File upload failed for '{file.filename}' in session {session_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@app.post("/uploads/finalize/{session_id}")
async def finalize_upload_endpoint(session_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Phase 3: The frontend calls this after all files are uploaded.
    This endpoint verifies that all files were received.
    """
    
    query = select(models.UploadedFile).where(
        models.UploadedFile.session_id == session_id,
        models.UploadedFile.status == "PENDING"
    )
    result = await db.execute(query)
    pending_files = result.scalars().all()

    if pending_files:
        missing_filenames = [f.filename for f in pending_files]
        logger.warning(f"Finalization failed for session {session_id}. Missing files: {missing_filenames}")
        raise HTTPException(
            status_code=400, 
            detail=f"Upload is incomplete. The following files were not received: {', '.join(missing_filenames)}"
        )
        
    logger.info(f"Successfully finalized upload for session {session_id}.")
    return {"success": True, "message": "All files have been successfully uploaded and the session is ready."}

# --- Orchestration Endpoints ---

@app.post("/orchestrate/analyze")
async def orchestrate_analyze(req: dict):
    job_id = str(uuid.uuid4())
    analyze_req = AnalyzeRequest(job_id=job_id, **req)
    async with httpx.AsyncClient() as client:
        try:
            # this call is returning almost instantly
            response = await client.post(f"{EXTRACTION_SERVICE_URL}/analyze", json=analyze_req.model_dump())
            response.raise_for_status()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

    # forward the job_id response to the frontend
    return {"job_id": job_id, "message": "Analysis job initiated."}
    
@app.post("/orchestrate/extract", status_code=202)
async def orchestrate_extraction(req: dict):
    """Starts an extraction job by calling the ExtractionService."""
    job_id = str(uuid.uuid4())
    extraction_req = ExtractionJobRequest(job_id=job_id, **req)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{EXTRACTION_SERVICE_URL}/extract", json=extraction_req.model_dump())
            response.raise_for_status() # Ensure the job was accepted
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            
    return {"job_id": job_id, "message": "Extraction job initiated."}

@app.post("/orchestrate/index", status_code=202)
async def orchestrate_indexing(req: dict):
    """Starts an indexing job by calling the QueryService."""
    job_id = str(uuid.uuid4())
    indexing_req = IndexJobRequest(job_id=job_id, **req)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{QUERY_SERVICE_URL}/index", json=indexing_req.model_dump())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

    return {"job_id": job_id, "message": "Indexing job initiated."}

@app.post("/orchestrate/query")
async def orchestrate_query(req: QueryRequest):
    """Proxies a query request directly to the QueryService."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{QUERY_SERVICE_URL}/query", json=req.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

@app.post("/orchestrate/update-schema")
async def orchestrate_update_schema(req: UpdateSchemaRequest):
    """Proxies a schema update request to the SchemaService."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{EXTRACTION_SERVICE_URL}/update-schema", json=req.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

@app.post("/generate-graph")
async def orchestrate_generate_graph(req: GraphGenerationRequest):
    """
    Orchestration endpoint to generate a knowledge graph.
    Proxies the request to the query-service.
    """
    try:        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{QUERY_SERVICE_URL}/generate-graph",
                json=req.model_dump()
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Error from query-service /generate-graph: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    except Exception as e:
        logger.error(f"Error in /generate-graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
# --- Status & Results Endpoints ---

@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Retrieves the current status and result of a completed job from Redis."""
    status = await job_manager.get_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JSONResponse(content=status)

@app.websocket("/ws/status/{job_id}")
async def websocket_status_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for streaming real-time job status updates.
    It listens to a Redis Pub/Sub channel for updates from worker services.
    """
    await websocket.accept()
    
    job_manager = JobStatusManager()
    channel = job_manager._get_pubsub_channel(job_id)
    
    # pubsub = job_manager.redis_client.pubsub()
    # await pubsub.subscribe(channel)
    
    try:
        # Send the initial status as soon as the client connects
        initial_status = await job_manager.get_status(job_id)
        if initial_status:
            await websocket.send_json(initial_status)
        else:
            await websocket.send_json({"status": "FAILED", "message": "Job not found."})
            return

        # Listen for new messages from the subscribed channel
        async with job_manager.redis_client.pubsub() as pubsub:
            await pubsub.subscribe(channel)
            
            # wait until a new message arrives
            async for message in pubsub.listen():
                if message and message["type"] == "message":
                    status_data = await job_manager.get_status(job_id) # Get the full status object
                    await websocket.send_json(status_data)
                
                    # If job is finished, close the connection
                    if status_data.get("status") in ["COMPLETED", "FAILED"]:
                        break

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from job {job_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket for job {job_id}: {e}", exc_info=True)
    finally:
        # pub/sub is automatically unsubscribed on exit from 'async with' block
        logger.info(f"WebSocket connection for job {job_id} closed.")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Proxies file download request to the Query Service."""
    async with httpx.AsyncClient() as client:
        try:
            # Make request to query service
            response = await client.get(
                f"{QUERY_SERVICE_URL}/download/{filename}",
                timeout=30.0  # Increase timeout for potentially large files
            )
            response.raise_for_status()
            
            # Stream the file content back to the client
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "text/csv"),
                headers={
                    "content-disposition": response.headers.get("content-disposition", f'attachment; filename="{filename}"')
                }
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error connecting to query service: {str(e)}")
        
@app.get("/session/{session_id}/data")
async def get_session_data(session_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieves all extracted data (records and schema) for a given session.
    """
    try:
        # --- 1. Fetch Session ---
        session = await db.get(models.Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        
        # --- 2. Fetch Records (Data) ---
        record_query = select(models.ExtractedRecord).where(
            models.ExtractedRecord.session_id == session_id
        ).order_by(models.ExtractedRecord.id)
        
        record_results = await db.execute(record_query)
        records = record_results.scalars().all()
        formatted_records = [r.data for r in records] 

        # --- 3. Build Fields List FROM Records (THIS IS THE FIX) ---
        all_field_names = set()
        if formatted_records:
            # Get all unique keys from all records
            for record in formatted_records:
                all_field_names.update(record.keys())
        
        # Get descriptions/types from the schema, if they exist
        schema_fields_map = {}
        if session.schema_details and session.schema_details.get("fields"):
             for f in session.schema_details.get("fields"):
                 if f.get("name"): # Ensure field has a name
                     schema_fields_map[f['name']] = f

        formatted_fields = []
        for field_name in sorted(list(all_field_names)):
            if field_name in schema_fields_map:
                # Use the rich data from the schema (with description, type)
                formatted_fields.append(schema_fields_map[field_name])
            else:
                # Fallback for fields in data but not schema (like _source_document)
                formatted_fields.append({
                    "name": field_name,
                    "type": "string", # Guess type
                    "description": ""
                })
        
        # --- 4. Fetch Metadata ---
        file_query = select(models.UploadedFile).where(
            models.UploadedFile.session_id == session_id,
            models.UploadedFile.status == "UPLOADED"
        )
        file_results = await db.execute(file_query)
        source_filenames = [f.filename for f in file_results.scalars().all()]

        # --- 5. Construct Final Response ---
        formatted_metadata = {
            "totalRecords": len(formatted_records),
            "source": ", ".join(source_filenames) if source_filenames else "N/A",
            "extractedAt": session.created_at.isoformat() 
        }

        return {
            "records": formatted_records,
            "fields": formatted_fields, # This list is now complete
            "metadata": formatted_metadata
        }

    except Exception as e:
        logger.error(f"Error fetching data for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching session data.")