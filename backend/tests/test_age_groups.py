from fastapi.testclient import TestClient

from backend.app.main import app

# Create a test client for the FastAPI app.
client = TestClient(app)

# Test that the age-groups endpoint returns:
# - HTTP 200
# - a list response
# - expected keys in the first item if data exists
def test_get_age_groups_success():
    response = client.get("/api/age-groups")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        first_row = data[0]
        assert "age_group_id" in first_row
        assert "age_bracket" in first_row