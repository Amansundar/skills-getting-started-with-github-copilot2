
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def reset_activities():
    """
    Helper to reset the activities' participants to their original state between tests.
    Ensures test isolation for in-memory data.
    """
    for activity in activities.values():
        # Remove all except original participants
        if "original_participants" in activity:
            activity["participants"] = list(activity["original_participants"])
        else:
            activity["original_participants"] = list(activity["participants"])

@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Pytest fixture to reset activities before and after each test.
    """
    reset_activities()
    yield
    reset_activities()

def test_get_activities():
    """
    Test GET /activities returns all activities.
    AAA: Arrange (none needed), Act (GET), Assert (response structure)
    """
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
    """
    Test successful signup for an activity.
    AAA: Arrange (new email), Act (POST), Assert (status and participant added)
    """
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

def test_signup_duplicate():
    """
    Test duplicate signup for an activity returns 400 error.
    AAA: Arrange (existing email), Act (POST), Assert (error response)
    """
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_invalid_activity():
    """
    Test signup for a nonexistent activity returns 404 error.
    AAA: Arrange (invalid activity), Act (POST), Assert (error response)
    """
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success():
    """
    Test successful unregistration from an activity.
    AAA: Arrange (registered email), Act (POST), Assert (status and participant removed)
    """
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """
    Test unregistration for a student not registered returns 400 error.
    AAA: Arrange (not registered), Act (POST), Assert (error response)
    """
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

def test_unregister_invalid_activity():
    """
    Test unregistration for a nonexistent activity returns 404 error.
    AAA: Arrange (invalid activity), Act (POST), Assert (error response)
    """
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
