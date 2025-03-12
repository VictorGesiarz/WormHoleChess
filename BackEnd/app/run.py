import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Adjust this to match your FastAPI file and app instance
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-restart on code changes (optional, useful in development)
        access_log=True,  # Explicitly enable access logs
        log_level="info",  # Set log level (debug, info, warning, error, critical)
    )
