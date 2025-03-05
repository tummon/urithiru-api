from datetime import datetime
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, UUID4
from typing import Annotated
from fastapi import Body


class Metric(str, Enum):
    WIND_SPEED = "wind_speed"
    TEMPERATURE = "temp"
    HUMIDITY = "humidity"


# Handle different units and their conversions
# Handle batch creating metrics
# Do better validation on value (negative wind speeds)
# Handle timestamps from the future
class SensorDataCreate(BaseModel):
    metric: Metric
    value: float
    sensor_id: UUID4
    timestamp: Annotated[datetime, Body(default_factory=lambda: datetime.now())]
    reading_id: Annotated[UUID4, Body(default_factory=lambda: uuid4())]
