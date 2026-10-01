import asyncio
import logging
import random
from fastapi import FastAPI, HTTPException, Query
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResilienceLogger")

app = FastAPI()

SIMULATE_FAULT = False


@app.get("/api/v1/users/{user_id}")
async def get_user_profile(user_id: int):
    delay = random.uniform(0.02, 0.10)
    await asyncio.sleep(delay)

    if random.random() < 0.01:
        raise HTTPException(status_code=500, detail="Database connection timeout")

    return {
        "id": user_id,
        "name": f"User_{user_id}",
        "status": "active"
    }


@app.get("/external-api/data")
async def external_service():
    if SIMULATE_FAULT:
        raise HTTPException(status_code=500, detail="External service is down!")
    return {"status": "success", "data": "Important Data"}


@app.post("/toggle-fault")
async def toggle_fault(enable: bool = Query(...)):
    global SIMULATE_FAULT
    SIMULATE_FAULT = enable
    return {"fault_injection_active": SIMULATE_FAULT}


@app.get("/api/v1/data-unprotected")
async def get_data_unprotected():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/external-api/data")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Unprotected call failed")
        return response.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0.5),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def fetch_external_data_with_retry():
    async with httpx.AsyncClient() as client:
        logger.info("Attempting external service call...")
        response = await client.get("http://localhost:8000/external-api/data", timeout=2.0)
        if response.status_code != 200:
            raise Exception("External API Error")
        return response.json()


@app.get("/api/v1/data-protected")
async def get_data_protected():
    try:
        data = await fetch_external_data_with_retry()
        return data
    except Exception as e:
        logger.warning(f"External service unavailable: {e}. Applied Fallback!")
        return {
            "status": "degraded",
            "data": "Cached Default Data (Fallback)",
            "is_fallback": True
        }