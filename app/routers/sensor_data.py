from fastapi import APIRouter, Query
from typing import Annotated
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery


router = APIRouter()

fake_items_db = [{"sensor_id": "1"}, {"sensor_id": "2"}, {"sensor_id": "3"}]


@router.get("/sensor-data")
async def read_sensor_data(sensor_data_query: Annotated[SensorDataQuery, Query()]):
    return fake_items_db


@router.post("/sensor-data", status_code=201)
async def create_sensor_data(sensor_data: SensorDataCreate):
    return sensor_data.model_dump_json()
