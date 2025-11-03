# /shared/aws_clients.py

import aioboto3
import os
import logging

logger = logging.getLogger(__name__)

# Get your S3 configuration from environment variables
S3_BUCKET_NAME = os.getenv("EXPORTS_BUCKET")

if not S3_BUCKET_NAME:
    logger.warning("Environment variable 'EXPORTS_BUCKET' is not set.")

# 1. Initialize the session at the module level
# This is lightweight and runs once when the module is imported.
session = aioboto3.Session()
logger.info("Successfully initialized Aioboto3 session.")