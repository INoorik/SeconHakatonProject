import uvicorn

from main import app as fastapi_app

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=5000, log_level="info")
