import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3

from app.config import (
    AWS_REGION,
    S3_BUCKET_NAME,
    SAGEMAKER_ENDPOINT_NAME,
    DYNAMODB_TABLE_NAME,
)

s3_client = boto3.client("s3", region_name=AWS_REGION)
runtime_client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
predictions_table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def upload_json_to_s3(data, key, bucket_name=S3_BUCKET_NAME):
    """
    Uploads a Python dictionary/list as a JSON object to S3.
    """
    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json"
    )
    return f"s3://{bucket_name}/{key}"


def invoke_sagemaker_endpoint(text, endpoint_name=SAGEMAKER_ENDPOINT_NAME):
    """
    Sends text to the SageMaker FinBERT endpoint and returns the model output.
    """
    payload = {"inputs": text}

    response = runtime_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=json.dumps(payload)
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    return result


def save_prediction_record(
    input_text,
    label,
    confidence,
    input_type="text",
    source="direct",
    s3_raw_key=None,
    s3_processed_key=None,
    headline=None,
    url=None,
):
    """
    Saves a summary prediction record in DynamoDB.
    """
    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    item = {
    "prediction_id": prediction_id,
    "timestamp": timestamp,
    "input_type": input_type,
    "input_text": input_text,
    "headline": headline or "",
    "url": url or "",
    "label": label,
    "confidence": Decimal(str(confidence)),
    "source": source,
    "s3_raw_key": s3_raw_key or "",
    "s3_processed_key": s3_processed_key or "",
}

    predictions_table.put_item(Item=item)
    return item