import uvicorn
from main import app as fastapi_app
from database_api import create_tables, database_connection

if __name__ == "__main__":
    create_tables(database_connection)
    uvicorn.run(fastapi_app, host="127.0.0.1", port=5000, log_level="info")