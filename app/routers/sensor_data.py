from datetime import datetime
from typing import List
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


@router.get("/sensor_data")
async def read_sensor_data(
    metric: List[Metric] = Query(),
    statistic: Statistic = Query(),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    sensor_id: List[str] | None = Query(None),
):
    return fake_items_db
