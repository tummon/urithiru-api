from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key
from ..models.sensor_data_create import SensorDataCreate
from ..models.sensory_data_query import SensorDataQuery


class SensorDataRepository:
    def __init__(self, dynamodb_resource: ServiceResource):
        self.table = dynamodb_resource.Table("WeatherData")

    def create_sensor_data(self, sensor_data: SensorDataCreate):
        partition_key = f"{sensor_data.sensor_id}#{sensor_data.metric}"
        self.table.put_item(
            Item={
                "sensor_id_metric": partition_key,
                "timestamp": sensor_data.timestamp.isoformat(),
                "sensor_id": sensor_data.sensor_id,
                "metric": sensor_data.metric,
                "value": sensor_data.value,
            }
        )
        return {
            "sensor_id_metric": partition_key,
            "timestamp": sensor_data.timestamp.isoformat(),
        }

    def query_sensor_data(self, sensor_data_query: SensorDataQuery):
        start = sensor_data_query.start_time.isoformat()
        end = sensor_data_query.end_time.isoformat()

        results = []
        if not sensor_data_query.sensor_id:
            for m in sensor_data_query.metric:
                data = self.__query_sensor_data_by_metric_gsi(m, start, end)
                results.extend(data)

            return results

        for sensor in sensor_data_query.sensor_id:
            for m in sensor_data_query.metric:
                data = self.__query_sensor_data_composite(
                    sensor,
                    m,
                    start,
                    end,
                )
                results.extend(data)

        return results

    def __query_sensor_data_composite(
        self, sensor_id: str, metric: str, start_time: str, end_time: str
    ):
        composite_partition_key = f"{sensor_id}#{metric}"
        response = self.table.query(
            KeyConditionExpression=Key("sensor_id_metric").eq(composite_partition_key)
            & Key("timestamp").between(start_time, end_time)
        )
        return response.get("Items", [])

    def __query_sensor_data_by_metric_gsi(
        self, metric: str, start_time: str, end_time: str
    ):
        response = self.table.query(
            IndexName="metrics-timestamp-index",
            KeyConditionExpression=Key("metric").eq(metric)
            & Key("timestamp").between(start_time, end_time),
        )
        return response.get("Items", [])
