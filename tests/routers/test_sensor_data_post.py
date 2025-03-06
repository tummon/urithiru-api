from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_post_sensor_data_wrong_metric():
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wrong",
            "value": 45.2,
            "sensor_id": "085b796f-d59e-4c7e-afab-a2b38205db7f",
        },
    )
    assert response.status_code == 422


def test_post_sensor_data():
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wind_speed",
            "value": 45.2,
            "sensor_id": "085b796f-d59e-4c7e-afab-a2b38205db7f",
        },
    )
    assert response.status_code == 201


def test_post_sensor_data_non_uuid_sensor_id():
    response = client.post(
        "/v1/api/sensor-data",
        json={
            "metric": "wind_speed",
            "value": 45.2,
            "sensor_id": "10",
        },
    )
    assert response.status_code == 422


def test_post_sensor_data_misformatted_timestamp():
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
