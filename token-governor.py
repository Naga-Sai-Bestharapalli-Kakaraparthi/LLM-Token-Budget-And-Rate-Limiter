from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time

app = FastAPI()

# Simple In-Memory Token Bucket Tracking (User ID -> { tokens_left, last_refill })
TOKEN_BUCKET_CAPACITY = 10000  # Max tokens per window
REFILL_RATE_PER_SEC = 100       # Token replenishment rate
user_buckets = {}

class LLMRequestPayload(BaseModel):
    user_id: str
    prompt: str
    estimated_tokens: int

def check_and_consume_budget(user_id: str, requested_tokens: int) -> bool:
    current_time = time.time()
    
    if user_id not in user_buckets:
        user_buckets[user_id] = {
            "tokens": TOKEN_BUCKET_CAPACITY,
            "last_update": current_time
        }
    
    bucket = user_buckets[user_id]
    
    # Refill tokens based on elapsed time
    elapsed = current_time - bucket["last_update"]
    bucket["tokens"] = min(TOKEN_BUCKET_CAPACITY, bucket["tokens"] + int(elapsed * REFILL_RATE_PER_SEC))
    bucket["last_update"] = current_time
    
    # Check if user has enough budget
    if bucket["tokens"] >= requested_tokens:
        bucket["tokens"] -= requested_tokens
        return True
    
    return False

@app.post("/api/v1/enforce-budget")
def enforce_token_budget(payload: LLMRequestPayload):
    allowed = check_and_consume_budget(payload.user_id, payload.estimated_tokens)
    
    if not allowed:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded: LLM token budget exhausted for this window."
        )
        
    return {
        "status": "APPROVED",
        "user_id": payload.user_id,
        "tokens_consumed": payload.estimated_tokens,
        "remaining_bucket_capacity": user_buckets[payload.user_id]["tokens"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
