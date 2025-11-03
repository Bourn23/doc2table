import os
import csv
from datetime import datetime
import asyncio
from typing import List, Dict, Any
from agents import Runner
from random import random
import functools
from shared.api_types import MaxRetriesExceededError

# storage handling
from botocore.exceptions import ClientError
from shared.aws_client import session, S3_BUCKET_NAME
import io

import logging
logger = logging.getLogger(__name__)

# ============================================================================
# Helper Functions
# ============================================================================
def create_column_chunks_from_data(
    extracted_data: List[Dict[str, Any]],
    columns_to_index: List[str]
) -> Dict[str, str]:
    """Creates a dictionary of {column_name: chunk_text} for specified columns."""
    column_chunks = {}
    for col in columns_to_index:
        chunk_text = f"All data for the column '{col.replace('_', ' ').title()}':\n\n"
        entries = []
        for i, record in enumerate(extracted_data):
            if col in record and record[col]:
                # Including the record ID helps link back to the full record
                entries.append(f"- Record ID {i}: {record[col]}")
        
        if entries:
            chunk_text += "\n".join(entries)
            column_chunks[col] = chunk_text
            
    return column_chunks


def create_text_chunks_from_data(extracted_data: List[Dict[str, Any]]) -> List[str]:
    """Converts extracted data into formatted string chunks for RAG"""
    chunks = []
    for i, record in enumerate(extracted_data):
        chunk_text = f"Record ID: {i}\n"
        chunk_text += "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in record.items()
        )
        chunks.append(chunk_text)
    return chunks



def async_retry(max_retries: int = 3, timeout_seconds: int = 30, initial_delay: int = 2):
    """
    A decorator to add timeout and exponential backoff retry logic
    to an asynchronous function.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    print(f"Attempt {attempt + 1}/{max_retries} for '{func.__name__}' timed out.")
                    if attempt == max_retries - 1:
                        raise MaxRetriesExceededError(
                            f"Function '{func.__name__}' failed after {max_retries} attempts."
                        )
                    delay = (initial_delay * (2 ** attempt)) + random()
                    print(f"Waiting {delay:.2f} seconds before retrying...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

@async_retry(max_retries=3, timeout_seconds=60)
async def run_agent_gracefully(agent, input_text):
    """
    A simple wrapper function to run the agent.
    The @async_retry decorator automatically handles timeouts and retries for this call.
    """
    print(f"Running agent: {agent.name}...")
    return await Runner.run(agent, input=input_text)


async def export_to_csv(records: List[Dict[str, any]], filename: str = "lumina_export") -> Dict[str, any]:
    """
    Exports extracted records to CSV format.

    Args:
        records: List of dictionaries containing extracted data
        filename: Base filename for the CSV (without extension)

    Returns:
        Dictionary with:
        - success: Boolean indicating if export succeeded
        - filepath: Path to the exported CSV file
        - message: Human-readable result message
    """
    try:
        if not records or len(records) == 0:
            return {
                "success": False,
                "message": "No data to export. Please extract data first.",
                "filepath": None
            }

        # Create exports directory if it doesn't exist
        os.makedirs("/data/exports", exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("/data/exports", f"{filename}_{timestamp}.csv")

        # Get field names from first record
        fieldnames = list(records[0].keys())

        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"✅ Exported {len(records)} records to {filepath}")

        return {
            "success": True,
            "filepath": filepath,
            "message": f"Successfully exported {len(records)} records to {os.path.basename(filepath)}",
            "record_count": len(records)
        }

    except Exception as e:
        print(f"❌ CSV export failed: {e}")
        return {
            "success": False,
            "message": f"Export failed: {str(e)}",
            "filepath": None
        }

async def export_to_s3(records: list[dict], filename: str = "lumina_export") -> dict:
    """
    Exports extracted records to a CSV string, then uploads it directly
    to S3 asynchronously.
    """
    try:
        if not records:
            return {"success": False, "message": "No data to export.", "s3_key": None}

        # --- 1. Create CSV in-memory (This part is sync, but very fast) ---
        fieldnames = list(records[0].keys())
        
        # Create an in-memory text buffer
        output_buffer = io.StringIO()
        
        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
        # Get the complete CSV string from the buffer
        csv_content_string = output_buffer.getvalue()
        output_buffer.close()

        # --- 2. Asynchronously upload to S3 ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{filename}_{timestamp}.csv"

        # Use the shared session to create an async client
        async with session.client("s3") as s3_client:
            await s3_client.put_object(
                Body=csv_content_string.encode('utf-8'), # S3 expects bytes
                Bucket=S3_BUCKET_NAME,
                Key=s3_key
            )

        logger.info(f"✅ Exported {len(records)} records to s3://{S3_BUCKET_NAME}/{s3_key}")

        return {
            "success": True,
            "s3_key": s3_key,
            "message": f"Successfully exported {len(records)} records to {s3_key}",
            "record_count": len(records)
        }

    except ClientError as e:
        logger.error(f"❌ S3 export failed: {e}", exc_info=True)
        return {"success": False, "message": f"S3 export failed: {str(e)}", "s3_key": None}
    except Exception as e:
        logger.error(f"❌ CSV generation failed: {e}", exc_info=True)
        return {"success": False, "message": f"CSV generation failed: {str(e)}", "s3_key": None}