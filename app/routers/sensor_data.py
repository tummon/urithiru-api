from fastapi import APIRouter

router = APIRouter()

fake_items_db = [{"sensor_id": "1"}, {"sensor_id": "2"}, {"sensor_id": "3"}]


@router.get("/sensor_data/")
async def read_sensor_data():
    return fake_items_db
