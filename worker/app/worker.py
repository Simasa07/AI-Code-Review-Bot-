import os
from celery import Celery
import google.generativeai as genai

from .database import SessionLocal
from .models import Review
from .github_client import get_pr_diff, post_pr_comment

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

celery_app = Celery("review_bot_worker", broker=REDIS_URL, backend=REDIS_URL)

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Used only when GITHUB_TOKEN isn't set yet, so local testing still works
# without a real GitHub connection.
SAMPLE_CODE_DIFF = """
def add_numbers(a, b):
    result = a+b
    return result

def divide(a, b):
    return a / b
"""


@celery_app.task
def ping():
    """Sanity-check task, kept from the first setup step."""
    return "pong"


def ask_gemini_for_review(code_diff: str) -> str:
    """Sends a piece of code to Google Gemini and gets back review comments."""
    model = genai.GenerativeModel("gemini-3.5-flash")
    prompt = (
        "You are a helpful, friendly code reviewer leaving comments on a GitHub "
        "pull request. Review the following code diff. Point out real bugs, "
        "style issues, and possible improvements. Keep it concise and kind, "
        "like a supportive teammate -- not harsh or nitpicky.\n\n"
        f"```\n{code_diff}\n```"
    )
    response = model.generate_content(prompt)
    return response.text


@celery_app.task(name="app.worker.process_review")
def process_review(review_id: int):
    """
    Picks up a queued review job:
      1. Fetches the real PR diff from GitHub (or a sample, if no token is set yet)
      2. Asks Gemini to review it
      3. Posts the feedback back onto the PR (if a real GitHub token is set)
      4. Saves the result and marks the review done
    """
    db = SessionLocal()
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return

        review.status = "in_progress"
        db.commit()

        try:
            if GITHUB_TOKEN:
                diff = get_pr_diff(review.repo_full_name, review.pr_number)
            else:
                diff = SAMPLE_CODE_DIFF

            feedback = ask_gemini_for_review(diff)

            if GITHUB_TOKEN:
                post_pr_comment(review.repo_full_name, review.pr_number, feedback)

            review.feedback = feedback
            review.status = "done"
        except Exception as e:
            review.status = "failed"
            review.feedback = f"Something went wrong: {e}"

        db.commit()
    finally:
        db.close()
