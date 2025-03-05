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
    response = client.get("/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1")
    assert response.status_code == 200


def test_get_sensor_data_with_multiple_sensor_id():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2"
    )
    assert response.status_code == 200


def test_get_sensor_data_with_bad_start_timestamp():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2&start_time=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_bad_end_timestamp():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&sensor_id=1&sensor_id=2&end_time=badtimestamp"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_correct_timestamps():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-02T19:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 200


def test_get_sensor_data_with_timestamps_that_are_longer_than_max_range_apart():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-01-02T19:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_timestamps_that_are_longer_than_min_range_apart():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-04T16:13:28.934213&end_time=2025-03-04T19:13:28.934213"
    )
    assert response.status_code == 422


def test_get_sensor_data_with_timestamps_where_end_time_is_before_start_time():
    response = client.get(
        "/v1/api/sensor-data?metric=temp&statistic=avg&start_time=2025-03-02T19:13:28.934213&end_time=2025-03-01T19:13:28.934213"
    )
    assert response.status_code == 422
