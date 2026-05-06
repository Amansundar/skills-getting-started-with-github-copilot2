import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state between tests
def reset_activities():
    for activity in activities.values():
        # Remove all except original participants
        if "original_participants" in activity:
            activity["participants"] = list(activity["original_participants"])
        else:
            activity["original_participants"] = list(activity["participants"])

@pytest.fixture(autouse=True)
def run_around_tests():
    reset_activities()
    yield
    reset_activities()

def test_get_activities():
    # Arrange
    # (No setup needed, uses default in-memory data)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_invalid_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
