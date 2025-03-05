#!/usr/bin/env python3

import boto3
import argparse

parser = argparse.ArgumentParser(description="Delete a DynamoDB table.")
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
        endpoint_url="http://localhost:8000",
        aws_access_key_id="fakeKeyId",
        aws_secret_access_key="fakeAccessKey",
        region_name="eu-west-1",
    )

table = dynamodb.Table("WeatherData")
table.delete()
table.wait_until_not_exists()

print("Table 'WeatherData' deleted successfully.")
