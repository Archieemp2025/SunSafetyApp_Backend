from fastapi.testclient import TestClient

from backend.app.main import app

# Create a test client for the FastAPI app.
client = TestClient(app)


# Test that the UV yearly summary endpoint returns:
# - HTTP 200
# - a list response
# - expected keys in the first item if data exists
def test_get_uv_year_summary_success():
    response = client.get("/api/uv/year-summary")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        first_row = data[0]
        assert "year" in first_row
        assert "australian_uv_low" in first_row
        assert "australian_uv_high" in first_row
        assert "australian_uv_median" in first_row