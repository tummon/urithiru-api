#!/usr/bin/env python3

import boto3
import argparse
import sys
import os

DYNAMO_DB_TABLE = "WeatherData"

# Default to creating the table locally, but offer the option of creating the
# table in an instance running in AWS.
parser = argparse.ArgumentParser(description="Create a DynamoDB table.")
parser.add_argument(
    "--remote",
    action="store_true",
    help="Use AWS-hosted DynamoDB instead of local instance",
)
args = parser.parse_args()

if args.remote:
    dynamodb = boto3.resource("dynamodb")
else:
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=os.getenv("AWS_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

existing_tables = dynamodb.meta.client.list_tables()["TableNames"]

if DYNAMO_DB_TABLE in existing_tables:
    print(f"Table '{DYNAMO_DB_TABLE}' already exists.")
    sys.exit(0)

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName=DYNAMO_DB_TABLE,
    KeySchema=[
        {"AttributeName": "sensor_id_metric", "KeyType": "HASH"},
        {"AttributeName": "timestamp", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "sensor_id_metric", "AttributeType": "S"},
        {"AttributeName": "timestamp", "AttributeType": "S"},
        {"AttributeName": "metric", "AttributeType": "S"},
    ],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "metrics-timestamp-index",
            "KeySchema": [
                {"AttributeName": "metric", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "Projection": {
                "ProjectionType": "ALL",
            },
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        }
    ],
    ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
)

# Wait until the table exists.
table.wait_until_exists()
print(table.item_count)
