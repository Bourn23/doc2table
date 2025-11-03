import redis
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

    def create_job(self, job_id: str, service: str = "general"):
        """
        Creates a new job record in Redis with a 'PENDING' status.
        """
        status_data = {
            "job_id": job_id,
            "service": service,
            "status": "PENDING",
            "message": "Job has been created and is waiting to be processed.",
            "timestamp": time.time(),
            "result": None,
        }
        
        # Using HSET to store the job as a dictionary (hash) in Redis.
        # This is efficient for updating individual fields later.
        self.redis_client.hset(
            self._get_status_key(job_id),
            mapping={k: json.dumps(v) for k, v in status_data.items()}
        )
        # Publish a message to notify listeners that the job status has changed.
        self.redis_client.publish(self._get_pubsub_channel(job_id), "status_updated")

    def update_status(self, job_id: str, status: str, message: str, result: Optional[Dict[str, Any]] = None):
        """
        Updates the status, message, and optional result of an existing job.
        
        Args:
            job_id: The unique ID of the job.
            status: The new status (e.g., "PROCESSING", "COMPLETED", "FAILED").
            message: A user-friendly message describing the current state.
            result: (Optional) A dictionary containing the final result of the job.
        """
        updates = {
            "status": json.dumps(status.upper()),
            "message": json.dumps(message),
            "timestamp": json.dumps(time.time()),
        }
        if result is not None:
            updates["result"] = json.dumps(result)
            
        self.redis_client.hset(self._get_status_key(job_id), mapping=updates)
        self.redis_client.publish(self._get_pubsub_channel(job_id), "status_updated")

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the complete status and result for a given job ID.
        
        Returns:
            A dictionary with the job's data, or None if the job is not found.
        """
        status_raw = self.redis_client.hgetall(self._get_status_key(job_id))
        
        if not status_raw:
            return None
            
        # Decode keys and JSON-decode values from Redis bytes
        return {
            k.decode('utf-8'): json.loads(v)
            for k, v in status_raw.items()
        }
        
    # Asynchronous versions of the above methods for use in async contexts
    async def acreate_job(self, job_id: str, service: str = "general", **kwargs):
        """
        Creates a new job record in a separate thread. (ASYNCHRONOUS)
        """
        return await asyncio.to_thread(self.create_job, job_id, service, **kwargs)

    async def aupdate_status(self, job_id: str, status: str, message: str, result: Optional[Dict[str, Any]] = None):
        """
        Updates the status, message, and optional result in a separate thread. (ASYNCHRONOUS)
        """
        return await asyncio.to_thread(self.update_status, job_id, status, message, result)
    
    async def aget_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the complete status and result in a separate thread. (ASYNCHRONOUS)
        """
        return await asyncio.to_thread(self.get_status, job_id)