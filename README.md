# Prerequisites:
- Docker
- Python >= 3.10

# Preparation:
Run `python3 -m venv .venv` to create a virtual environment  
Run `pip install -r requirements.txt` to install dependencies.

# Start the API (and DB if using local)
Run `docker-compose up` to start dynamodb locally, or you can use configured AWS credentials to access in AWS.  

On the initial run you will need to create the table in DynamoDB.  

Run `./create_dynamodb_table.py` to create the table locally. Run `./create_dynamodb_table.py --remote` to create in your configured AWS account.  
Run `./delete_dynamodb_table.py` to delete the table locally. Run `./delete_dynamodb_table.py --remote` to delete in your configured AWS account.  

Run `fastapi dev --port 8001` to start the api. (Using Port 8001 incase local dynamodb is used which uses 8000)  

Open http://localhost:8001/docs in your browser to see the OpenAPI documentation and make some requests.  
