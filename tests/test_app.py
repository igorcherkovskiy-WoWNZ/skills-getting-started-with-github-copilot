from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of initial participants and restore after each test
    original = {k: v.copy() for k, v in activities.items()}
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_prevention():
    client = TestClient(app)
    email = "teststudent@mergington.edu"
    activity = "Chess Club"

    # Sign up should succeed
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # Signing up again should return 400
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400


def test_unregister_participant():
    client = TestClient(app)
    # Use an existing participant from the fixture data
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]

    res = client.delete(f"/activities/{activity}/signup?email={participant}")
    assert res.status_code == 200
    assert participant not in activities[activity]["participants"]


def test_unregister_nonexistent():
    client = TestClient(app)
    res = client.delete("/activities/Chess Club/signup?email=nosuch@mergington.edu")
    assert res.status_code == 404
