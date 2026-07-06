import os

from app import PRODUCT_IMAGE_DIR, app


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


def test_product_without_image_file_falls_back_to_icon():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert 'src="/static/images/products/roxylean.jpg"' not in body
    assert "product-thumb" in body


def test_product_with_image_file_renders_photo():
    image_path = os.path.join(PRODUCT_IMAGE_DIR, "roxylean.jpg")
    with open(image_path, "wb") as f:
        f.write(b"fake-image-bytes")
    try:
        client = app.test_client()
        response = client.get("/products")
        body = response.data.decode()
        assert 'src="/static/images/products/roxylean.jpg"' in body
    finally:
        os.remove(image_path)
