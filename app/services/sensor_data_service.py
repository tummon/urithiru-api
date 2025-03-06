from ..repositories.sensor_data_repo import SensorDataRepository
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery, Statistic
from typing import List
from decimal import Decimal

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
        for d in data:
            sensor_id = d["sensor_id"]
            metric = d["metric"]
            value = d["value"]
            if sensor_id not in result:
                result[sensor_id] = {}
            if metric not in result[sensor_id]:
                result[sensor_id][metric] = []
            result[sensor_id][metric].append(value)

        for s_id, v in result.items():
            for m, v2 in v.items():
                result[s_id][m] = apply_statistic(v2, sensor_data_query.statistic)

        return result
