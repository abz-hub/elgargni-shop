from app import app


def test_index_returns_ok():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_brand_and_services():
    client = app.test_client()
    response = client.get("/")
    body = response.data.decode()
    assert "Elgargni Shop" in body
    assert "Protein" in body
    assert "Recovery" in body
