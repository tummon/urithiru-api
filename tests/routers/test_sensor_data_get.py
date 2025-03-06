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


def test_get_sensor_data_wrong_metric_validation(client):
    response = client.get("/v1/api/sensor-data?metric=wrong&statistic=avg")
    assert response.status_code == 422


def test_get_sensor_data_wrong_statistic_validation(client):
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=wrong")
    assert response.status_code == 422


def test_get_sensor_data_no_statistic_validation(client):
    response = client.get("/v1/api/sensor-data?metric=temp")
    assert response.status_code == 422


def test_get_sensor_data_no_metric_validation(client):
    response = client.get("/v1/api/sensor-data?statistic=avg")
    assert response.status_code == 422


def test_get_sensor_data(client):
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=avg")
    assert response.status_code == 200


def test_get_sensor_data_with_sensor_id(client):
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1")
    assert response.status_code == 200


def test_get_sensor_data_with_multiple_sensor_id(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2"
    )
    assert response.status_code == 200


def test_get_sensor_data_with_bad_start_timestamp(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2&start_time=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_bad_end_timestamp(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2&end_time=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_correct_timestamps(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-02T19:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 200


def test_get_sensor_data_with_timestamps_that_are_longer_than_max_range_apart(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-01-02T19:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_timestamps_that_are_longer_than_min_range_apart(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-04T16:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_timestamps_where_end_time_is_before_start_time(client):
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-02T19:13:28.934213&end_time=2025-03-01T19:13:28.934213"
    )
    assert response.status_code == 422
