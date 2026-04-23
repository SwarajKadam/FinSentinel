from pathlib import Path
from typing import Any, Dict

import boto3
import json

from app.config import AWS_REGION, SAGEMAKER_ENDPOINT_NAME


def upload_to_s3(file_path: str, bucket_name: str, object_name: str | None = None) -> dict:
    """
    Simple starter helper for future AWS deployment.
    This uploads a local file to S3 using boto3.
    """
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    final_object_name = object_name or Path(file_path).name

    s3_client.upload_file(file_path, bucket_name, final_object_name)
    return {"message": "Upload complete", "bucket": bucket_name, "object_name": final_object_name}


def invoke_sagemaker_endpoint(payload: Dict[str, Any]) -> dict:
    """
    Simple starter helper for future AWS deployment.
    This can later send text to a SageMaker endpoint for inference.
    """
    runtime_client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)

    response = runtime_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload).encode("utf-8"),
    )

    return {
        "status_code": response["ResponseMetadata"]["HTTPStatusCode"],
        "body": response["Body"].read().decode("utf-8"),
    }
