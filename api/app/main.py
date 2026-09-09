import hashlib
import hmac
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from .celery_client import celery_client
from .database import Base, engine, get_db
from .models import Review

app = FastAPI(title="AI Code Review Bot API")

# Create the "reviews" table if it doesn't exist yet.
Base.metadata.create_all(bind=engine)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Checks that this request really came from GitHub, using our shared secret."""
    if not WEBHOOK_SECRET:
        # No secret configured yet (early local dev) -- skip the check for now.
        return True
    if not signature_header:
        return False
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "AI Code Review Bot API is running"}


@app.post("/webhook")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = request.headers.get("X-GitHub-Event", "")
    if event != "pull_request":
        return {"message": f"Ignored event type: {event}"}

    payload = await request.json()
    action = payload.get("action")
    if action not in ("opened", "synchronize", "reopened"):
        return {"message": f"Ignored PR action: {action}"}

    pr = payload["pull_request"]
    review = Review(
        repo_full_name=payload["repository"]["full_name"],
        pr_number=pr["number"],
        status="pending",
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Hand the slow work off to the background worker and respond to GitHub immediately.
    celery_client.send_task("app.worker.process_review", args=[review.id])

    return {"message": "Review queued", "review_id": review.id}


@app.get("/reviews/{review_id}")
def get_review_status(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {
        "id": review.id,
        "repo": review.repo_full_name,
        "pr_number": review.pr_number,
        "status": review.status,
        "feedback": review.feedback,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
    }
