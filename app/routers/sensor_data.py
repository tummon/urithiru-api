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
    return sensor_data_service.query_sensor_data(sensor_data_query)


@router.post("/sensor-data", status_code=201)
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    sensor_data_service: Annotated[SensorDataService, Depends(get_sensor_data_service)],
):
    return sensor_data_service.create_sensor_data(sensor_data)
