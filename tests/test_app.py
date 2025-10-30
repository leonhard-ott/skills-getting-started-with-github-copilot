import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities

def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up test@mergington.edu for Chess Club"}

    # Verify the student was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_duplicate_signup():
    """Test that a student cannot sign up for the same activity twice"""
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    
    # Try to sign up again
    response = client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    email = "unregister@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}

    # Verify the student was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_registered():
    """Test unregistering when not registered"""
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}