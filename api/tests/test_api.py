from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.main.celery_client.send_task")
def test_webhook_queues_a_review_for_opened_pr(mock_send_task):
    payload = {
        "action": "opened",
        "pull_request": {"number": 7},
        "repository": {"full_name": "someone/some-repo"},
    }
    response = client.post(
        "/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Review queued"
    assert "review_id" in body

    # Confirm we handed the job off to the worker via Celery.
    mock_send_task.assert_called_once()
    args, kwargs = mock_send_task.call_args
    assert args[0] == "app.worker.process_review"


def test_webhook_ignores_non_pull_request_events():
    response = client.post(
        "/webhook",
        json={},
        headers={"X-GitHub-Event": "issues"},
    )
    assert response.status_code == 200
    assert "Ignored" in response.json()["message"]


def test_webhook_ignores_irrelevant_pr_actions():
    payload = {
        "action": "closed",
        "pull_request": {"number": 7},
        "repository": {"full_name": "someone/some-repo"},
    }
    response = client.post(
        "/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert response.status_code == 200
    assert "Ignored" in response.json()["message"]


def test_review_status_not_found_returns_404():
    response = client.get("/reviews/999999")
    assert response.status_code == 404
