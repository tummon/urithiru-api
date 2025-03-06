FROM python:3.13.0

WORKDIR /urithiru-api

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/
COPY scripts/ scripts/
EXPOSE 8001
CMD [ "fastapi", "run", "--port", "8001" ]