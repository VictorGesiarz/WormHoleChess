import uvicorn
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=args.port,
        reload=True,
        access_log=True,
        log_level="info",
    )
