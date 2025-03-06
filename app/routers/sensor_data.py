from fastapi import APIRouter, Query, Depends
from typing import Annotated
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery
from ..services.sensor_data_service import SensorDataService
from .dependencies import get_sensor_data_service


router = APIRouter()

fake_items_db = [{"sensor_id": "1"}, {"sensor_id": "2"}, {"sensor_id": "3"}]


@router.get("/sensor-data")
async def read_sensor_data(
    sensor_data_query: Annotated[SensorDataQuery, Query()],
    sensor_data_service: Annotated[SensorDataService, Depends(get_sensor_data_service)],
):
    """
    Query a sensor data readings:

    - **sensor_id**: this is a list of UUID4 uuid. Here are some
        - db858a5c-2b2a-4ddf-967d-5940c4632c5b
        - 69c10414-2f70-462c-9693-7e761f3b3a76
        - a4c835f5-91b7-4810-bf3a-b7cfa96dce2e
        - 18677714-e71e-4cda-bbf4-858f5fe87ab4
        - 84e5d68f-5e0e-434e-9cf5-c0fbfe42659b
    - **start_time**: this should be isoformat in utc timezone please
    - **end_time**: this should be isoformat in utc timezone please
    - **metric (REQUIRED)**: list of metrics: humidity, temp, wind_speed
    - **statistic (REQUIRED)**: one statistic: avg, sum, min, max
    """
    return sensor_data_service.query_sensor_data(sensor_data_query)


@router.post("/sensor-data", status_code=201)
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    sensor_data_service: Annotated[SensorDataService, Depends(get_sensor_data_service)],
):
    """
    Create a sensor data reading:

    - **sensor_id**: this should be a UUID4 uuid. Here are some
        - db858a5c-2b2a-4ddf-967d-5940c4632c5b
        - 69c10414-2f70-462c-9693-7e761f3b3a76
        - a4c835f5-91b7-4810-bf3a-b7cfa96dce2e
        - 18677714-e71e-4cda-bbf4-858f5fe87ab4
        - 84e5d68f-5e0e-434e-9cf5-c0fbfe42659b
    - **timestamp**: this should be isoformat in utc timezone please
    - **metric**: humidity, temp, wind_speed
    - **value**: float/decimal value
    """
    return sensor_data_service.create_sensor_data(sensor_data)
