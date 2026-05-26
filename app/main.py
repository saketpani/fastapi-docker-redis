import os
import logging
from fastapi import FastAPI, HTTPException
import redis

# Setup enterprise-level tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ProductionAPI")

app = FastAPI(title="Containerized Data Ingress Hub")

# Ingress environment parameters
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize the global connection pool abstraction layer
# Since Docker guarantees Redis is up, we can connect natively on application boot
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    r.ping()
    logger.info("✓ Application context securely attached to Redis connection pool.")
except redis.exceptions.ConnectionError as conn_err:
    logger.critical(f"Bootstrapping Failed: Immediate network denial to cache layer: {str(conn_err)}")
    raise RuntimeError("Critical infrastructure component unavailable.") from conn_err

@app.get("/")
def home():
    try:
        # Atomic increment command
        count = r.incr("counter")
        return {
            "message": "Hello from FastAPI + Docker + Redis!",
            "count": count
        }
    except Exception as e:
        logger.error(f"Transaction Fault: Counter execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database transaction processing error.")

@app.get("/health")
def health():
    try:
        r.ping()
        return {
            "status": "healthy",
            "redis": "connected",
            "engine": "FastAPI Container Running Non-Root"
        }
    except Exception as e:
        logger.error(f"Health Telemetry Breakdown: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection dropped: {str(e)}"
        )