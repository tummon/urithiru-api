# Prerequisites:
- Docker

# Start the API and DB
Run `docker-compose up --build`

Open http://localhost:8001/docs in your browser to see the OpenAPI documentation and make some requests.  

You can use openapi docs page to test queries.

# Running the tests
I didn't get around to running the tests in docker, so you'll need to manually run these.
Only tested with Python 3.13.0, but I think anything 3.10+ should be ok.

```bash
# Setup virtual env
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run pytest
pytest

# When finished deactivate the venv
deactivate
```