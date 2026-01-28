import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app, activities


def test_get_root(client):
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that activities endpoint returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have activities
    assert len(data) > 0
    
    # Check that each activity has the expected fields
    for activity_name, activity_details in data.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_signup_for_activity(client):
    """Test signing up a new student for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]


def test_signup_duplicate_student(client):
    """Test that duplicate signup is rejected"""
    # First signup should succeed
    response = client.post(
        "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
    )
    assert response.status_code == 200
    
    # Second signup with same email should fail
    response = client.post(
        "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signup for nonexistent activity fails"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity"""
    # First signup
    client.post(
        "/activities/Programming%20Class/signup?email=unregister@mergington.edu"
    )
    
    # Then unregister
    response = client.delete(
        "/activities/Programming%20Class/unregister?email=unregister@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "unregister@mergington.edu" in data["message"]


def test_unregister_nonexistent_student(client):
    """Test that unregistering a non-existent student fails"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client):
    """Test that unregistering from nonexistent activity fails"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_activity_participants_updated(client):
    """Test that participant count is updated correctly"""
    email = "participant@mergington.edu"
    
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()["Gym Class"]["participants"])
    
    # Sign up
    client.post(f"/activities/Gym%20Class/signup?email={email}")
    
    # Check updated count
    response = client.get("/activities")
    updated_count = len(response.json()["Gym Class"]["participants"])
    assert updated_count == initial_count + 1
