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


def test_products_returns_ok():
    client = app.test_client()
    response = client.get("/products")
    assert response.status_code == 200


def test_products_lists_all_items():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert "Whey HD" in body
    assert "Salted Caramel" in body
    assert "RoxyLean" in body
    assert "290 LYD" in body
