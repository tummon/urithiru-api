from ..repositories.sensor_data_repo import SensorDataRepository
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery, Statistic
from typing import List
from decimal import Decimal
from itertools import groupby
from operator import itemgetter


def apply_statistic(data: List[Decimal], statistic: Statistic):
    match statistic:
        case Statistic.AVERAGE:
            return sum(data) / len(data)
        case Statistic.SUM:
            return sum(data)
        case Statistic.MINIMUM:
            return min(data)
        case Statistic.MAXIMUM:
            return max(data)


class SensorDataService:
    def __init__(self, sensor_data_repo: SensorDataRepository):
        self.sensor_data_repo = sensor_data_repo

    def create_sensor_data(self, sensor_data: SensorDataCreate):
        return self.sensor_data_repo.create_sensor_data(sensor_data)

    # Output looks like
    # {
    #     sensor_id_1: {
    #         humidity: calculated_statistic_value,
    #         temp: calculated_statistic_value,
    #         ...
    #     },
    #     sensor_id_2: {
    #         wind_speed: calculated_statistic_value,
    #         humidity: calculated_statistic_value,
    #         ...
    #     },
    #     ...
    # }
    def query_sensor_data(self, sensor_data_query: SensorDataQuery):
        data = self.sensor_data_repo.query_sensor_data(sensor_data_query)
        result = {}
        # Group the data by sensor_id
        for id_key, id_group in groupby(data, key=itemgetter("sensor_id")):
            result[id_key] = {}

            # Group the above groups into metric groups
            for metric_key, metric_group in groupby(id_group, key=itemgetter("metric")):
                # Map these into just the values so we can run the statistic on them
                values = list(map(lambda d: d.get("value", 0), metric_group))
                result[id_key][metric_key] = apply_statistic(
                    values, sensor_data_query.statistic
                )
        return result
