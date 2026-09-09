from unittest.mock import MagicMock, patch

from app.database import Base, SessionLocal, engine
from app.models import Review
from app.worker import ask_gemini_for_review, process_review

Base.metadata.create_all(bind=engine)


@patch("app.worker.genai.GenerativeModel")
def test_ask_gemini_for_review_returns_model_text(mock_model_cls):
    mock_instance = MagicMock()
    mock_instance.generate_content.return_value.text = "Looks good, nice job!"
    mock_model_cls.return_value = mock_instance

    result = ask_gemini_for_review("def add(a, b): return a + b")

    assert result == "Looks good, nice job!"
    mock_instance.generate_content.assert_called_once()


@patch("app.worker.post_pr_comment")
@patch("app.worker.get_pr_diff")
@patch("app.worker.genai.GenerativeModel")
def test_process_review_marks_done_and_saves_feedback(
    mock_model_cls, mock_get_diff, mock_post_comment
):
    mock_get_diff.return_value = "diff --git a/app.py b/app.py"
    mock_instance = MagicMock()
    mock_instance.generate_content.return_value.text = "Nice, clean code!"
    mock_model_cls.return_value = mock_instance

    db = SessionLocal()
    review = Review(repo_full_name="someone/some-repo", pr_number=3, status="pending")
    db.add(review)
    db.commit()
    db.refresh(review)
    review_id = review.id
    db.close()

    import app.worker as worker_module

    original_token = worker_module.GITHUB_TOKEN
    worker_module.GITHUB_TOKEN = "fake-token-for-test"
    try:
        process_review(review_id)
    finally:
        worker_module.GITHUB_TOKEN = original_token

    db = SessionLocal()
    updated = db.query(Review).filter(Review.id == review_id).first()
    db.close()

    assert updated.status == "done"
    assert updated.feedback == "Nice, clean code!"
    mock_get_diff.assert_called_once_with("someone/some-repo", 3)
    mock_post_comment.assert_called_once()


@patch("app.worker.genai.GenerativeModel")
def test_process_review_marks_failed_on_error(mock_model_cls):
    mock_model_cls.side_effect = RuntimeError("Gemini is unreachable")

    db = SessionLocal()
    review = Review(repo_full_name="someone/some-repo", pr_number=4, status="pending")
    db.add(review)
    db.commit()
    db.refresh(review)
    review_id = review.id
    db.close()

    process_review(review_id)

    db = SessionLocal()
    updated = db.query(Review).filter(Review.id == review_id).first()
    db.close()

    assert updated.status == "failed"
    assert "Something went wrong" in updated.feedback
