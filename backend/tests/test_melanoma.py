from fastapi.testclient import TestClient

from backend.app.main import app

# Create a test client for the FastAPI app.
client = TestClient(app)


# Test a valid melanoma incidence request. The current expected default age-group example is 20-29
def test_get_melanoma_incidence_success():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Persons",
            "age_group": "20-29",
            "year_from": 2007,
            "year_to": 2023,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        first_row = data[0]
        assert "year" in first_row
        assert "count" in first_row

# Test that an invalid age-group value is rejected.
def test_get_melanoma_incidence_invalid_age_group():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Persons",
            "age_group": "All ages combined",
            "year_from": 2007,
            "year_to": 2023,
        },
    )

    assert response.status_code == 400

# Test that an invalid year ordering is rejected.
def test_get_melanoma_incidence_invalid_year_order():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Persons",
            "age_group": "20-29",
            "year_from": 2023,
            "year_to": 2007,
        },
    )

    assert response.status_code == 400


# Test that years below the supported range are rejected.
def test_get_melanoma_incidence_year_below_range():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Persons",
            "age_group": "20-29",
            "year_from": 2006,
            "year_to": 2023,
        },
    )

    assert response.status_code == 422

# Test that years above the supported range are rejected.
def test_get_melanoma_incidence_year_above_range():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Persons",
            "age_group": "20-29",
            "year_from": 2007,
            "year_to": 2024,
        },
    )

    assert response.status_code == 422

# Test that an invalid sex value is rejected.
def test_get_melanoma_incidence_invalid_sex():
    response = client.get(
        "/api/melanoma/incidence",
        params={
            "sex": "Unknown",
            "age_group": "20-29",
            "year_from": 2007,
            "year_to": 2023,
        },
    )

    assert response.status_code == 400