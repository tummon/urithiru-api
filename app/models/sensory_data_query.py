from datetime import datetime, timedelta
from typing import Self, Annotated, List
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from .sensor_data_create import Metric

MAX_RANGE_LENGTH = 30
MIN_RANGE_LENGTH = 1


class Statistic(str, Enum):
    AVERAGE = "avg"
    MINIMUM = "min"
    MAXIMUM = "max"
    SUM = "sum"


class SensorDataQuery(BaseModel):
    model_config = {"extra": "forbid"}

    metric: Annotated[List[Metric], Field()]
    statistic: Annotated[Statistic, Field()]
    sensor_id: Annotated[List[str] | None, Field()] = None
    start_time: Annotated[datetime | None, Field()] = None
    end_time: Annotated[datetime | None, Field()] = None

    @model_validator(mode="after")
    def check_start_is_before_end(self) -> Self:
        # If we don't have one end of the range, ignore this check
        if self.start_time is None or self.end_time is None:
            return self

        if self.start_time >= self.end_time:
            raise ValueError("Start time is after the provided end time")

        return self

    @model_validator(mode="after")
    def check_range_length(self) -> Self:
        # If we don't have one end of the range, ignore this check
        if self.start_time is None or self.end_time is None:
            return self

        range_length = self.end_time - self.start_time
        if range_length < timedelta(days=MIN_RANGE_LENGTH):
            raise ValueError(f"Time range must be at least {MIN_RANGE_LENGTH} day")

        if range_length > timedelta(days=MAX_RANGE_LENGTH):
            raise ValueError(f"Time range cannot exceed {MAX_RANGE_LENGTH}")

        return self

    @model_validator(mode="after")
    def fill_date_range(self) -> Self:
        # If no range is filled, just take the latest max range
        if self.start_time is None and self.end_time is None:
            self.start_time = datetime.now() - timedelta(days=MAX_RANGE_LENGTH)
            self.end_time = datetime.now()
        # else if we have an end datetime with no start, we set the
        # start to the max range before the end
        elif self.start_time is None:
            self.start_time = self.end_time - timedelta(days=MAX_RANGE_LENGTH)
        # else if we have a start datetime with no end, we set the
        # max range possible without going past the current time.
        elif self.end_time is None:
            max_range_length_after_start = self.start_time + timedelta(
                days=MAX_RANGE_LENGTH
            )
            self.end_time = (
                max_range_length_after_start
                if max_range_length_after_start < datetime.now()
                else datetime.now()
            )

        return self
