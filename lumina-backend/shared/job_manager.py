import redis.asyncio as redis
import json
import time
import os
from typing import Dict, Any, Optional
import asyncio ## otherwise synchronous redis calls would block the event loop

class JobStatusManager:
    """
    Manages job status and results using Redis as a backend.
    
    This utility class provides a simple interface to create jobs, update their
    status, and store their final results. It communicates updates via Redis Pub/Sub,
    allowing other services (like an API gateway) to listen for real-time changes.
    """
    
    def __init__(self, redis_url: str = None):
        """
        Initializes the Redis client.
        
        Args:
            redis_url: The connection URL for Redis. Defaults to the REDIS_URL
                       environment variable or "redis://localhost:6379".
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        
        self.redis_client = redis.Redis.from_url(redis_url)

    def _get_status_key(self, job_id: str) -> str:
        """Returns the Redis key for storing a job's status hash."""
        return f"job:status:{job_id}"

    def _get_pubsub_channel(self, job_id: str) -> str:
        """Returns the Redis channel for publishing updates for a specific job."""
        return f"job_updates:{job_id}"

    async def create_job(self, job_id: str, service: str = "general", **kwargs):
        """
        Creates a new job record in Redis with a 'PENDING' status. (ASYNCHRONOUS)
        """
        status_data = {
            "job_id": job_id,
            "service": service,
            "status": "PENDING",
            "message": "Job has been created and is waiting to be processed.",
            "timestamp": time.time(),
            "result": None,
            **kwargs, # Pass in other data like session_id
        }
        
        mapping_data = {k: json.dumps(v) for k, v in status_data.items()}

        # Changed: Use an async pipeline for efficiency
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(
                self._get_status_key(job_id),
                mapping=mapping_data
            )
            pipe.publish(self._get_pubsub_channel(job_id), "status_updated")
            await pipe.execute() # Await the pipeline

    # Changed: Method is now 'async def'
    async def update_status(self, job_id: str, status: str, message: str, result: Optional[Dict[str, Any]] = None):
        """
        Updates the status, message, and optional result of an existing job. (ASYNCHRONOUS)
        """
        updates = {
            "status": json.dumps(status.upper()),
            "message": json.dumps(message),
            "timestamp": json.dumps(time.time()),
        }
        if result is not None:
            updates["result"] = json.dumps(result)
        
        # Changed: Use an async pipeline
        async with self.redis_client.pipeline() as pipe:
            pipe.hset(self._get_status_key(job_id), mapping=updates)
            pipe.publish(self._get_pubsub_channel(job_id), "status_updated")
            await pipe.execute()

    # Changed: Method is now 'async def'
    async def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the complete status and result for a given job ID. (ASYNCHRONOUS)
        """
        # Changed: 'await' the async call
        status_raw = await self.redis_client.hgetall(self._get_status_key(job_id))
        
        if not status_raw:
            return None
            
        # This part is CPU-bound (fast) and doesn't need to be async
        return {
            k.decode('utf-8'): json.loads(v)
            for k, v in status_raw.items()
        }