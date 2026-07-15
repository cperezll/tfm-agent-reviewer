
from fastapi import FastAPI


app = FastAPI(
    title="TFM Agent Reviewer",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "TFM Agent Reviewer is running"
    }