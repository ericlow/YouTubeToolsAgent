import uvicorn

from api.main import app

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",    # import main app definition
        host="0.0.0.0",         # listen on all network interfaces
        port=8000,              # listen on port 8000
        reload=True,            # watch python files for changes
        log_level="info"        # log level
    )