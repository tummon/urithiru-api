import pytest
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.sensor_data_repo import DYNAMO_DB_TABLE
from app.routers.dependencies import get_dynamodb_resource

########## WOOPSIE
# At the last second I realoised I forgot to add the mocking for the service and broke all my tests when I hooked the service into the endpoints,
# so instead at the last second I've just copied the dynamodb mocking here too. These are now integration tests too!
# But what I want to do it just mock the response from the service, and keep it as a unittest
##########


@pytest.fixture(scope="function")
def mock_dynamodb_resource():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
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
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.meta.client.get_waiter("table_exists").wait(TableName=DYNAMO_DB_TABLE)

        yield dynamodb


@pytest.fixture(scope="function")
def override_dependencies(mock_dynamodb_resource):
    """Override the FastAPI dependencies with test instances"""

    def get_test_dynamodb_resource():
        return mock_dynamodb_resource

    app.dependency_overrides[get_dynamodb_resource] = get_test_dynamodb_resource

    yield

    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def client(override_dependencies):
    return TestClient(app)


def test_post_sensor_data_wrong_metric(client):
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wrong",
            "value": 45.2,
            "sensor_id": "085b796f-d59e-4c7e-afab-a2b38205db7f",
        },
    )
    assert response.status_code == 422


def test_post_sensor_data(client):
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wind_speed",
            "value": 45.2,
            "sensor_id": "085b796f-d59e-4c7e-afab-a2b38205db7f",
        },
    )
    assert response.status_code == 201


def test_post_sensor_data_non_uuid_sensor_id(client):
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wind_speed",
            "value": 45.2,
            "sensor_id": "10",
        },
    )
    assert response.status_code == 422


def test_post_sensor_data_misformatted_timestamp(client):
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wind_speed",
            "value": 45.2,
            "sensor_id": "085b796f-d59e-4c7e-afab-a2b38205db7f",
            "timestamp": "wrong_format",
        },
    )
    assert response.status_code == 422
