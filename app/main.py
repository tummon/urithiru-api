from fastapi import FastAPI

from .routers import sensor_data

app = FastAPI()

# Adding sensor data router with prefix for API versioning
app.include_router(sensor_data.router, prefix="/v1/api")
