from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_sensor_data_wrong_metric_validation():
    response = client.get("/v1/api/sensor-data?metric=wrong&statistic=avg")
    assert response.status_code == 422


def test_get_sensor_data_wrong_statistic_validation():
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=wrong")
    assert response.status_code == 422


def test_get_sensor_data_no_statistic_validation():
    response = client.get("/v1/api/sensor-data?metric=temp")
    assert response.status_code == 422


def test_get_sensor_data_no_metric_validation():
    response = client.get("/v1/api/sensor-data?statistic=avg")
    assert response.status_code == 422


def test_get_sensor_data():
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=avg")
    assert response.status_code == 200


def test_get_sensor_data_with_sensor_id():
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=avg&sensor-id=1")
    assert response.status_code == 200


def test_get_sensor_data_with_multiple_sensor_id():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor-id=1&sensor-id=2"
    )
    assert response.status_code == 200


def test_get_sensor_data_with_bad_start_timestamp():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor-id=1&sensor-id=2&start=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_bad_end_timestamp():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor-id=1&sensor-id=2&end=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_timestamps():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start=2025-03-02T19:13:28.934213&end=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 200
