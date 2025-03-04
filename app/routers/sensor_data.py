from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Query

from enum import Enum


class Metric(str, Enum):
    WIND_SPEED = "wind_speed"
    TEMPERATURE = "temp"
    HUMIDITY = "humidity"


class Statistic(str, Enum):
    AVERAGE = "avg"
    MINIMUM = "min"
    MAXIMUM = "max"
    SUM = "sum"


router = APIRouter()

fake_items_db = [{"sensor_id": "1"}, {"sensor_id": "2"}, {"sensor_id": "3"}]


@router.get("/sensor-data")
async def read_sensor_data(
    metric: Annotated[List[Metric], Query()],
    statistic: Annotated[Statistic, Query()],
    start: Annotated[datetime | None, Query()] = None,
    end: Annotated[datetime | None, Query()] = None,
    sensor_id: Annotated[List[str] | None, Query(alias="sensor-id")] = None,
):
    return fake_items_db
