from fastapi import FastAPI, HTTPException
import redis
import os
import time

app = FastAPI()

RETRY_COUNT = int(os.getenv("RETRY_COUNT", 5))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

for i in range(RETRY_COUNT):
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        r.ping()
        print("Connected to Redis!")
        break

    except redis.exceptions.ConnectionError:
        print("Redis not ready, retrying...")
        time.sleep(2)

@app.get("/")
def home():
    count = r.incr("counter")

    return {
        "message": "Hello from FastAPI + Docker + Redis!",
        "count": count
    }

@app.get("/health")
def health():
    try:
        r.ping()

        return {
            "status": "healthy",
            "redis": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}"
        )