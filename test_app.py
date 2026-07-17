import json
import urllib.parse

import app as app_module
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


def test_product_without_image_file_falls_back_to_icon():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert 'src="/static/images/products/cla-carnitine-snow-cone.jpg"' not in body
    assert "product-thumb" in body


def test_product_with_image_file_renders_photo():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert 'src="/static/images/products/roxylean.webp"' in body


def test_shakers_category_lists_both_bpi_variants():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert 'id="shakers"' in body
    assert body.count("BPI Shaker") >= 2
    assert "Blue" in body
    assert "Clear" in body
    assert body.count("25 LYD") >= 2
    assert 'src="/static/images/products/bpi-shaker-blue.webp"' in body
    assert 'src="/static/images/products/bpi-shaker-clear.jpg"' in body


def test_shaker_can_be_added_to_cart():
    client = app.test_client()
    client.post("/cart/add/16", data={"quantity": "2"})
    response = client.get("/cart")
    body = response.data.decode()
    assert "BPI Shaker" in body
    assert "Qty: 2" in body
    assert "50 LYD" in body


def test_magnet_bags_category_lists_both_colors():
    client = app.test_client()
    response = client.get("/products")
    body = response.data.decode()
    assert 'id="magnet-bags"' in body
    assert body.count("Magnet Bag") >= 2
    assert "Pink" in body
    assert "Black" in body
    assert body.count("70 LYD") >= 2
    assert 'src="/static/images/products/magnet-bag-pink.jpg"' in body
    assert 'src="/static/images/products/magnet-bag-black.webp"' in body


def test_magnet_bag_can_be_added_to_cart():
    client = app.test_client()
    client.post("/cart/add/19", data={"quantity": "2"})
    response = client.get("/cart")
    body = response.data.decode()
    assert "Magnet Bag" in body
    assert "Black" in body
    assert "Qty: 2" in body
    assert "140 LYD" in body


def test_cart_add_and_view():
    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "2"})
    response = client.get("/cart")
    body = response.data.decode()
    assert "Whey HD" in body
    assert "Qty: 2" in body
    assert "1040 LYD" in body


def test_cart_remove():
    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    client.post("/cart/remove/1")
    response = client.get("/cart")
    assert "Your cart is empty" in response.data.decode()


def test_cart_add_ajax_returns_json_and_drawer():
    client = app.test_client()
    response = client.post(
        "/cart/add/1", data={"quantity": "2"}, headers={"X-Cart-Ajax": "1"}
    )
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["count"] == 2
    assert data["total"] == 1040
    assert "Whey HD" in data["drawer_html"]
    assert "cart-drawer-checkout" in data["drawer_html"]


def test_cart_remove_ajax_returns_empty_drawer():
    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"}, headers={"X-Cart-Ajax": "1"})
    response = client.post("/cart/remove/1", headers={"X-Cart-Ajax": "1"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 0
    assert "cart-drawer-empty" in data["drawer_html"]


def test_cart_add_without_ajax_still_redirects():
    client = app.test_client()
    response = client.post("/cart/add/1", data={"quantity": "1"})
    assert response.status_code == 302


def test_cart_button_and_drawer_present_on_pages():
    client = app.test_client()
    body = client.get("/products").data.decode()
    assert 'id="cart-button"' in body
    assert 'id="cart-drawer"' in body


def test_checkout_redirects_when_cart_empty():
    client = app.test_client()
    response = client.get("/checkout")
    assert response.status_code == 302


def test_checkout_shows_payment_methods():
    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.get("/checkout")
    body = response.data.decode()
    assert "Cash on Delivery" in body
    assert "Bank Transfer" in body
    assert "Coming soon" in body


def test_checkout_submit_with_cod_creates_order(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.post(
        "/checkout",
        data={
            "name": "Test Customer",
            "phone": "0912345678",
            "address": "Tripoli, Libya",
            "payment_method": "cod",
        },
    )
    body = response.data.decode()
    assert response.status_code == 200
    assert "Order Placed" in body

    saved_order = json.loads(orders_file.read_text().strip())
    assert saved_order["payment_method"] == "cod"
    assert saved_order["customer"]["name"] == "Test Customer"

    cart_response = client.get("/cart")
    assert "Your cart is empty" in cart_response.data.decode()


def test_checkout_rejects_unavailable_payment_method(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.post(
        "/checkout",
        data={
            "name": "Test Customer",
            "phone": "0912345678",
            "address": "Tripoli, Libya",
            "payment_method": "card",
        },
    )
    body = response.data.decode()
    assert "Please select a valid payment method" in body
    assert not orders_file.exists()


def test_subscribe_shows_plan_and_payment_methods():
    client = app.test_client()
    response = client.get("/subscribe")
    body = response.data.decode()
    assert "Full Coaching Plan" in body
    assert "120" in body
    assert "Cash on Delivery" in body


def test_subscribe_submit_creates_subscription(monkeypatch, tmp_path):
    subscriptions_file = tmp_path / "subscriptions.jsonl"
    monkeypatch.setattr(app_module, "SUBSCRIPTIONS_LOG_PATH", str(subscriptions_file))

    client = app.test_client()
    response = client.post(
        "/subscribe",
        data={"name": "Test Customer", "phone": "0912345678", "payment_method": "cod"},
    )
    body = response.data.decode()
    assert response.status_code == 200
    assert "Subscription Confirmed" in body

    saved = json.loads(subscriptions_file.read_text().strip())
    assert saved["payment_method"] == "cod"
    assert saved["customer"]["name"] == "Test Customer"
    assert saved["price"] == 120
    assert saved["plan"] == "full-coaching-plan"


def test_selected_coach_plan_renders_correct_name_and_price():
    client = app.test_client()
    response = client.get("/subscribe?plan_id=coach-seraj-algot")
    body = response.data.decode()
    assert "Seraj Algot" in body
    assert "250 LYD" in body
    assert 'name="plan_id" value="coach-seraj-algot"' in body

def test_waled_coach_plan_renders_existing_caption_and_price():
    client = app.test_client()
    response = client.get("/subscribe?plan_id=coach-waled-elgargni")
    body = response.data.decode()
    assert "Waled Elgargni" in body
    assert "250 LYD" in body
    assert 'name="plan_id" value="coach-waled-elgargni"' in body


def test_selected_coach_is_saved_with_subscription(monkeypatch, tmp_path):
    subscriptions_file = tmp_path / "subscriptions.jsonl"
    monkeypatch.setattr(app_module, "SUBSCRIPTIONS_LOG_PATH", str(subscriptions_file))

    client = app.test_client()
    response = client.post(
        "/subscribe",
        data={
            "name": "Coach Customer",
            "phone": "0912345678",
            "payment_method": "cod",
            "plan_id": "coach-hafed-abugrin",
        },
    )
    assert response.status_code == 200
    saved = json.loads(subscriptions_file.read_text().strip())
    assert saved["plan"] == "coach-hafed-abugrin"
    assert saved["coach_id"] == "hafed-abugrin"
    assert saved["plan_name"] == "Hafed Abugrin"
    assert saved["price"] == 250


def test_subscribe_rejects_missing_name(monkeypatch, tmp_path):
    subscriptions_file = tmp_path / "subscriptions.jsonl"
    monkeypatch.setattr(app_module, "SUBSCRIPTIONS_LOG_PATH", str(subscriptions_file))

    client = app.test_client()
    response = client.post(
        "/subscribe",
        data={"name": "", "phone": "0912345678", "payment_method": "cod"},
    )
    body = response.data.decode()
    assert "Name is required" in body
    assert not subscriptions_file.exists()


def test_default_language_is_english():
    client = app.test_client()
    response = client.get("/")
    body = response.data.decode()
    assert '<html lang="en" dir="ltr">' in body
    assert "Get strong with" in body


def test_set_language_to_arabic_switches_content_and_direction():
    client = app.test_client()
    client.get("/set-language/ar")
    response = client.get("/")
    body = response.data.decode()
    assert '<html lang="ar" dir="rtl">' in body
    assert "كن قويًا" in body
    assert "المنتجات" in body


def test_set_language_persists_across_pages():
    client = app.test_client()
    client.get("/set-language/ar")
    response = client.get("/products")
    body = response.data.decode()
    assert '<html lang="ar" dir="rtl">' in body
    assert "جميع المنتجات" in body


def test_set_language_rejects_invalid_code():
    client = app.test_client()
    client.get("/set-language/fr")
    response = client.get("/")
    body = response.data.decode()
    assert '<html lang="en" dir="ltr">' in body


def test_set_language_redirects_back_to_referrer():
    client = app.test_client()
    response = client.get("/set-language/ar", headers={"Referer": "http://localhost/products"})
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/products"


def test_order_does_not_notify_telegram_when_unconfigured(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    calls = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: calls.append(1))

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.post(
        "/checkout",
        data={"name": "T", "phone": "09", "address": "Tripoli", "payment_method": "cod"},
    )
    assert response.status_code == 200
    assert calls == []


def test_order_notifies_telegram_when_configured(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "99999")

    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["body"] = req.data.decode("utf-8")
        return None

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    client.post(
        "/checkout",
        data={"name": "Sara", "phone": "0910000000", "address": "Tripoli", "payment_method": "cod"},
    )

    assert "api.telegram.org/bottest-token/sendMessage" in captured["url"]
    text = urllib.parse.parse_qs(captured["body"])["text"][0]
    assert "New Order" in text
    assert "Sara" in text
    assert "Whey HD" in text


def test_order_still_succeeds_when_telegram_fails(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "99999")

    def boom(*a, **k):
        raise RuntimeError("telegram down")

    monkeypatch.setattr("urllib.request.urlopen", boom)

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.post(
        "/checkout",
        data={"name": "T", "phone": "09", "address": "Tripoli", "payment_method": "cod"},
    )
    assert response.status_code == 200
    assert "Order Placed" in response.data.decode()
    assert json.loads(orders_file.read_text().strip())["customer"]["name"] == "T"


def test_order_notifies_whatsapp_when_configured(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setenv("CALLMEBOT_APIKEY", "key123")
    monkeypatch.setenv("WHATSAPP_PHONE", "+218940000849")

    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req if isinstance(req, str) else req.full_url
        return None

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    client.post(
        "/checkout",
        data={"name": "Sara", "phone": "0910000000", "address": "Tripoli", "payment_method": "cod"},
    )

    assert "api.callmebot.com/whatsapp.php" in captured["url"]
    assert "key123" in captured["url"]
    assert "Sara" in urllib.parse.unquote_plus(captured["url"])


def test_order_notifies_both_channels_when_both_configured(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "1")
    monkeypatch.setenv("CALLMEBOT_APIKEY", "key123")
    monkeypatch.setenv("WHATSAPP_PHONE", "+218940000849")

    urls = []

    def fake_urlopen(req, timeout=None):
        urls.append(req if isinstance(req, str) else req.full_url)
        return None

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = app.test_client()
    client.post("/cart/add/1", data={"quantity": "1"})
    client.post(
        "/checkout",
        data={"name": "T", "phone": "09", "address": "Tripoli", "payment_method": "cod"},
    )

    joined = " ".join(urls)
    assert "api.telegram.org" in joined
    assert "api.callmebot.com" in joined


def test_coaching_team_renders_all_four_coaches_in_english():
    client = app.test_client()
    body = client.get("/").data.decode()
    assert 'id="coaches"' in body
    assert "Waled Elgargni" in body
    assert "Mohammed Alsaid" in body
    assert "Seraj Algot" in body
    assert "Hafed Abugrin" in body
    assert body.count("250") >= 4
    assert 'src="/static/images/coach.png"' in body
    assert 'src="/static/images/coaches/mohammed-alsaid.jpeg"' in body
    assert 'src="/static/images/coaches/seraj-algot.jpeg"' in body
    assert 'src="/static/images/coaches/hafed-abugrin.jpeg"' in body


def test_coaching_team_renders_in_arabic_rtl():
    client = app.test_client()
    client.get("/set-language/ar")
    body = client.get("/").data.decode()
    assert '<html lang="ar" dir="rtl">' in body
    assert "وليد عبدالسلام القرقني" in body
    assert "محمد الصيد" in body
    assert "سراج القط" in body
    assert "حفيظ أبوقرين" in body


def test_whatsapp_button_renders_with_business_number():
    client = app.test_client()
    response = client.get("/")
    body = response.data.decode()
    assert "https://wa.me/218940000849" in body
    assert 'class="whatsapp-btn"' in body


def test_whatsapp_message_is_translated():
    client = app.test_client()
    en_body = client.get("/").data.decode()
    assert "Hello%2C%20I%20have%20a%20question" in en_body

    client.get("/set-language/ar")
    ar_body = client.get("/").data.decode()
    assert "wa.me/218940000849" in ar_body
    assert "%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D9%8B" in ar_body


def test_arabic_checkout_shows_translated_errors(monkeypatch, tmp_path):
    orders_file = tmp_path / "orders.jsonl"
    monkeypatch.setattr(app_module, "ORDERS_LOG_PATH", str(orders_file))

    client = app.test_client()
    client.get("/set-language/ar")
    client.post("/cart/add/1", data={"quantity": "1"})
    response = client.post(
        "/checkout",
        data={"name": "", "phone": "", "address": "", "payment_method": "cod"},
    )
    body = response.data.decode()
    assert "الاسم مطلوب" in body
    assert not orders_file.exists()


def test_calculators_page_returns_ok():
    client = app.test_client()
    response = client.get("/calculators")
    assert response.status_code == 200


def test_calculators_page_contains_form_options():
    client = app.test_client()
    response = client.get("/calculators")
    body = response.data.decode()
    assert "Muscle Gain" in body
    assert "Weight Loss" in body
    assert "Cutting" in body
    assert "Performance" in body
    assert "Sedentary" in body
    assert "Moderate Activity" in body


def test_calculators_page_contains_all_recommendation_sets():
    client = app.test_client()
    response = client.get("/calculators")
    body = response.data.decode()
    # muscle set
    assert 'data-goal="muscle"' in body
    # cut/lose shared set
    assert 'data-goal="cut"' in body
    assert 'data-goal="lose"' in body
    # performance set
    assert 'data-goal="performance"' in body
    assert "Whey HD" in body
    assert "Micronized Creatine" in body
    assert "ISO HD" in body
    assert "CLA + Carnitine" in body
    assert "1.M.R The OG Formula" in body


def test_calculators_recommendation_add_to_cart_links_are_real():
    client = app.test_client()
    response = client.get("/calculators")
    body = response.data.decode()
    assert 'action="/cart/add/1"' in body
    assert 'action="/cart/add/8"' in body
    assert 'action="/cart/add/6"' in body
    assert 'action="/cart/add/14"' in body
    assert 'action="/cart/add/11"' in body


def test_calculators_nav_link_present():
    client = app.test_client()
    response = client.get("/")
    body = response.data.decode()
    assert 'href="/calculators"' in body
    assert "Calculators" in body


def test_calculators_page_in_arabic():
    client = app.test_client()
    client.get("/set-language/ar")
    response = client.get("/calculators")
    body = response.data.decode()
    assert '<html lang="ar" dir="rtl">' in body
    assert "زيادة عضل" in body
    assert "الحاسبات" in body
