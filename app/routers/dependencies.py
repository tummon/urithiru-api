from fastapi import Depends
from typing import Annotated
import boto3
from boto3.resources.base import ServiceResource
from ..repositories.sensor_data_repo import SensorDataRepository
from ..services.sensor_data_service import SensorDataService


def get_dynamodb_resource():
    # if args.remote:
    #     dynamodb = boto3.resource("dynamodb")
    # else:
    return boto3.resource(
        "dynamodb",
        endpoint_url="http://localhost:8000",
        aws_access_key_id="fakeKeyId",
        aws_secret_access_key="fakeAccessKey",
        region_name="eu-west-1",
    )


def get_sensor_data_repo(
    dynamodb: Annotated[ServiceResource, Depends(get_dynamodb_resource)],
):
    return SensorDataRepository(dynamodb)


def get_sensor_data_service(
    sensor_data_repo: Annotated[SensorDataRepository, Depends(get_sensor_data_repo)],
):
    return SensorDataService(sensor_data_repo)
