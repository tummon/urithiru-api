import pytest
import boto3
from datetime import datetime, timezone, timedelta
from moto import mock_aws
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.sensor_data_repo import DYNAMO_DB_TABLE
from app.models.sensory_data_query import Statistic
from app.models.sensor_data_create import Metric
from app.routers.dependencies import get_dynamodb_resource

SENSOR_ID_1 = "802a4627-89ea-4529-aef5-d155e39fd800"
SENSOR_ID_2 = "a6150afc-15f7-4d55-b227-f11de61b620b"
SENSOR_ID_3 = "35a557ba-05ff-42a7-9545-951f2c2ee8f2"
BASE_TIME = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


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


@pytest.fixture(scope="function")
def sample_data(client):
    sensor_data_list = [
        # sensor 1
        {
            "metric": Metric.TEMPERATURE,
            "value": 22.5,
            "sensor_id": SENSOR_ID_1,
            "timestamp": (BASE_TIME - timedelta(days=35)).isoformat(),
        },
        {
            "metric": Metric.TEMPERATURE,
            "value": 20.0,
            "sensor_id": SENSOR_ID_1,
            "timestamp": (BASE_TIME - timedelta(days=15)).isoformat(),
        },
        {
            "metric": Metric.TEMPERATURE,
            "value": 23.8,
            "sensor_id": SENSOR_ID_1,
            "timestamp": (BASE_TIME).isoformat(),
        },
        # sensor 2
        {
            "metric": Metric.HUMIDITY,
            "value": 45.0,
            "sensor_id": SENSOR_ID_2,
            "timestamp": (BASE_TIME - timedelta(days=15)).isoformat(),
        },
        {
            "metric": Metric.HUMIDITY,
            "value": 48.2,
            "sensor_id": SENSOR_ID_2,
            "timestamp": (BASE_TIME - timedelta(days=10)).isoformat(),
        },
        {
            "metric": Metric.HUMIDITY,
            "value": 50.5,
            "sensor_id": SENSOR_ID_2,
            "timestamp": (BASE_TIME - timedelta(days=5)).isoformat(),
        },
        # sensor 3
        {
            "metric": Metric.TEMPERATURE,
            "value": 6.1,
            "sensor_id": SENSOR_ID_3,
            "timestamp": (BASE_TIME - timedelta(days=20)).isoformat(),
        },
        {
            "metric": Metric.TEMPERATURE,
            "value": 3.3,
            "sensor_id": SENSOR_ID_3,
            "timestamp": (BASE_TIME - timedelta(days=12)).isoformat(),
        },
        {
            "metric": Metric.TEMPERATURE,
            "value": 0.5,
            "sensor_id": SENSOR_ID_3,
            "timestamp": (BASE_TIME - timedelta(days=8)).isoformat(),
        },
        {
            "metric": Metric.WIND_SPEED,
            "value": 23.1,
            "sensor_id": SENSOR_ID_3,
            "timestamp": (BASE_TIME - timedelta(days=3)).isoformat(),
        },
        {
            "metric": Metric.WIND_SPEED,
            "value": 3.2,
            "sensor_id": SENSOR_ID_3,
            "timestamp": (BASE_TIME - timedelta(days=1)).isoformat(),
        },
    ]

    for data in sensor_data_list:
        response = client.post("v1/api/sensor-data", json=data)
        assert response.status_code == 201

    return sensor_data_list


def test_get_sensor_data_without_params(client):
    response = client.get("/v1/api/sensor-data")
    assert response.status_code == 422


def test_get_max_sensor_data_of_sensor_1_in_the_last_30_days(client, sample_data):
    response = client.get(
        "/v1/api/sensor-data",
        params={
            "sensor_id": SENSOR_ID_1,
            "metric": Metric.TEMPERATURE.value,
            "statistic": Statistic.MAXIMUM.value,
            "end_time": BASE_TIME.isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {SENSOR_ID_1: {Metric.TEMPERATURE.value: 23.8}}


def test_get_max_sensor_data_of_sensor_1_in_the_30_days_before_10_days_ago(
    client, sample_data
):
    response = client.get(
        "/v1/api/sensor-data",
        params={
            "sensor_id": SENSOR_ID_1,
            "metric": Metric.TEMPERATURE.value,
            "statistic": Statistic.MAXIMUM.value,
            "end_time": (BASE_TIME - timedelta(days=10)).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {SENSOR_ID_1: {Metric.TEMPERATURE.value: 22.5}}


def test_get_max_sensor_data_of_sensor_1_between_10_and_30_days_ago(
    client, sample_data
):
    response = client.get(
        "/v1/api/sensor-data",
        params={
            "sensor_id": SENSOR_ID_1,
            "metric": Metric.TEMPERATURE.value,
            "statistic": Statistic.MAXIMUM.value,
            "end_time": (BASE_TIME - timedelta(days=10)).isoformat(),
            "start_time": (BASE_TIME - timedelta(days=30)).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {SENSOR_ID_1: {Metric.TEMPERATURE.value: 20}}


def test_get_sum_of_wind_speed_temp_and_humidity_for_all_sensors_in_last_30_days(
    client, sample_data
):
    response = client.get(
        "/v1/api/sensor-data",
        params={
            "metric": [
                Metric.TEMPERATURE.value,
                Metric.WIND_SPEED.value,
                Metric.HUMIDITY.value,
            ],
            "statistic": Statistic.SUM.value,
            "end_time": BASE_TIME.isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        SENSOR_ID_1: {Metric.TEMPERATURE.value: 43.8},
        SENSOR_ID_2: {Metric.HUMIDITY.value: 143.7},
        SENSOR_ID_3: {Metric.TEMPERATURE.value: 9.9, Metric.WIND_SPEED.value: 26.3},
    }
