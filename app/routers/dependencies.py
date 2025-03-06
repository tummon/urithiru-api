from fastapi import Depends
from typing import Annotated
import boto3
from boto3.resources.base import ServiceResource
from ..repositories.sensor_data_repo import SensorDataRepository
from ..services.sensor_data_service import SensorDataService
from ..config import AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_REGION, AWS_SECRET_KEY


def get_dynamodb_resource():
    # if args.remote:
    #     dynamodb = boto3.resource("dynamodb")
    # else:
    return boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )


def get_sensor_data_repo(
    dynamodb: Annotated[ServiceResource, Depends(get_dynamodb_resource)],
):
    return SensorDataRepository(dynamodb)


def get_sensor_data_service(
    sensor_data_repo: Annotated[SensorDataRepository, Depends(get_sensor_data_repo)],
):
    return SensorDataService(sensor_data_repo)
