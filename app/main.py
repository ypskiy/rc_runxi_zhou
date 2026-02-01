from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from app.tasks import deliver_notification
from app.config import REDIS_URL, VENDOR_CONFIGS
import uuid

app = FastAPI(title="Notification Gateway MVP")
redis_conn = Redis.from_url(REDIS_URL)
# User default queue
q = Queue('default', connection=redis_conn)

class NotificationRequest(BaseModel):
    vendor_id: str
    payload: dict
    idempotency_key: str = None

@app.post("/api/v1/notify")
async def enqueue_notification(req: NotificationRequest):
    # 1. Validate Vendor
    if req.vendor_id not in VENDOR_CONFIGS:
        raise HTTPException(status_code=400, detail="Unknown Vendor ID")

    # 2. Idempotency Key
    job_id = req.idempotency_key or str(uuid.uuid4())

    # 3. Enqueue
    try:
        job = q.enqueue(
            deliver_notification,
            args=(req.vendor_id, req.payload),
            job_id=job_id,
            result_ttl=86400,
            retry=None # Retry handled inside the task
        )
        return {"status": "accepted", "job_id": job.id, "queue_position": len(q)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Queue Service Unavailable: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}
