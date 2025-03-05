from ..repositories.sensor_data_repo import SensorDataRepository
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery


class SensorDataService:
    def __init__(self, sensor_data_repo: SensorDataRepository):
        self.sensor_data_repo = sensor_data_repo

    def create_sensor_data(self, sensor_data: SensorDataCreate):
        return self.sensor_data_repo.create_sensor_data(sensor_data)

    def query_sensor_data(self, sensor_data_query: SensorDataQuery):
        return self.sensor_data_repo.query_sensor_data(sensor_data_query)
