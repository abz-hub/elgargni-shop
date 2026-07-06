import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

PRODUCT_IMAGE_DIR = os.path.join(app.static_folder, "images", "products")
ORDERS_LOG_PATH = os.path.join(os.path.dirname(__file__), "orders.jsonl")
SUBSCRIPTIONS_LOG_PATH = os.path.join(os.path.dirname(__file__), "subscriptions.jsonl")

SUBSCRIPTION_PLAN = {
    "name": "Full Coaching Plan",
    "price": 120,
    "billing_period": "month",
    "features": [
        "Personalized monthly diet and meal plan",
        "Regular check-ins and progress tracking",
        "Supplement guidance tailored to your goals",
        "Direct access to your coach",
    ],
}

CATEGORIES = ["Protein & Recovery", "Pre-Workout & Energy", "Vitamins & Wellness"]


def slugify(category):
    return category.lower().replace(" & ", "-").replace(" ", "-")


SERVICES = [
    {
        "title": "Protein & Recovery",
        "description": "Whey, casein, and BCAAs to rebuild and recover after every session.",
    },
    {
        "title": "Pre-Workout & Energy",
        "description": "Clean energy blends to help you push harder and last longer.",
    },
    {
        "title": "Vitamins & Wellness",
        "description": "Daily essentials to keep you performing at your peak, every day.",
    },
]
for service in SERVICES:
    service["slug"] = slugify(service["title"])

PRODUCTS = [
    {"id": 1, "name": "Whey HD", "flavor": "Chocolate Cookie", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-chocolate-cookie.jpg"},
    {"id": 2, "name": "Whey HD", "flavor": "Strawberry Cake", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-strawberry-cake.jpg"},
    {"id": 3, "name": "Whey HD", "flavor": "Milk and Cookies", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-milk-and-cookies.jpg"},
    {"id": 4, "name": "Whey HD", "flavor": "Blueberry Muffin", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-blueberry-muffin.jpg"},
    {"id": 5, "name": "Whey HD", "flavor": "Salted Caramel", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-salted-caramel.jpg"},
    {"id": 6, "name": "ISO HD", "flavor": "Cookies and Cream", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery", "image": "iso-hd-cookies-and-cream.jpg"},
    {"id": 7, "name": "ISO HD", "flavor": "Chocolate Brownie", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery", "image": "iso-hd-chocolate-brownie.jpg"},
    {"id": 8, "name": "Micronized Creatine", "flavor": "Unflavored", "size": "1.32 lbs (600g)", "price": 370, "category": "Protein & Recovery", "image": "micronized-creatine-unflavored.webp"},
    {"id": 9, "name": "Best BCAA", "flavor": "Fruit Punch", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy", "image": "best-bcaa-fruit-punch.webp"},
    {"id": 10, "name": "Best BCAA", "flavor": "Watermelon Ice", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy", "image": "best-bcaa-watermelon-ice.webp"},
    {"id": 11, "name": "1.M.R The OG Formula", "flavor": "Fruit Punch", "size": "12.1 oz (342.5g)", "price": 340, "category": "Pre-Workout & Energy", "image": "1mr-og-fruit-punch.webp"},
    {"id": 12, "name": "1.M.R The OG Formula", "flavor": "Sour Gummy", "size": "12.2 oz (346g)", "price": 340, "category": "Pre-Workout & Energy", "image": "1mr-og-sour-gummy.webp"},
    {"id": 13, "name": "CLA + Carnitine", "flavor": "Snow Cone", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness", "image": "cla-carnitine-snow-cone.jpg"},
    {"id": 14, "name": "CLA + Carnitine", "flavor": "Rainbow Ice", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness", "image": "cla-carnitine-rainbow-ice.webp"},
    {"id": 15, "name": "RoxyLean", "flavor": "Fat Burner & Thermogenic", "size": "60 capsules", "price": 290, "category": "Vitamins & Wellness", "image": "roxylean.webp"},
]
PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

PAYMENT_METHODS = [
    {
        "id": "cod",
        "label": "Cash on Delivery",
        "description": "Pay in cash when your order arrives at your door.",
        "available": True,
    },
    {
        "id": "bank_transfer",
        "label": "Bank Transfer",
        "description": "Transfer the total to our bank account and use your order number as the reference.",
        "available": True,
    },
    {
        "id": "card",
        "label": "Credit / Debit Card",
        "description": "Coming soon — our team will contact you to complete payment securely.",
        "available": False,
    },
    {
        "id": "mobile_wallet",
        "label": "Mobile Wallet",
        "description": "Coming soon.",
        "available": False,
    },
]
PAYMENT_METHODS_BY_ID = {m["id"]: m for m in PAYMENT_METHODS}


def product_image_url(product):
    if os.path.exists(os.path.join(PRODUCT_IMAGE_DIR, product["image"])):
        return f"images/products/{product['image']}"
    return None


def get_cart_items():
    cart = session.get("cart", {})
    items = []
    for product_id_str, quantity in cart.items():
        product = PRODUCTS_BY_ID.get(int(product_id_str))
        if not product:
            continue
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": product["price"] * quantity,
            }
        )
    return items


def get_cart_total(items):
    return sum(item["subtotal"] for item in items)


@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES, plan=SUBSCRIPTION_PLAN, currency="LYD")


@app.route("/products")
def products():
    grouped = [
        {
            "name": category,
            "slug": slugify(category),
            "products": [
                {**p, "image_path": product_image_url(p)}
                for p in PRODUCTS
                if p["category"] == category
            ],
        }
        for category in CATEGORIES
    ]
    return render_template("products.html", grouped=grouped, currency="LYD")


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id):
    if product_id not in PRODUCTS_BY_ID:
        abort(404)
    quantity = request.form.get("quantity", type=int) or 1
    quantity = max(1, quantity)
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    session["cart"] = cart
    return redirect(request.referrer or url_for("products"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    items = get_cart_items()
    total = get_cart_total(items)
    return render_template("cart.html", items=items, total=total, currency="LYD")


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = get_cart_items()
    if not items:
        return redirect(url_for("products"))
    total = get_cart_total(items)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        address = (request.form.get("address") or "").strip()
        payment_method = PAYMENT_METHODS_BY_ID.get(request.form.get("payment_method"))

        errors = []
        if not name:
            errors.append("Name is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not address:
            errors.append("Delivery address is required.")
        if not payment_method or not payment_method["available"]:
            errors.append("Please select a valid payment method.")

        if errors:
            return render_template(
                "checkout.html",
                items=items,
                total=total,
                currency="LYD",
                payment_methods=PAYMENT_METHODS,
                errors=errors,
                form=request.form,
            )

        order = {
            "order_id": uuid.uuid4().hex[:8].upper(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "customer": {"name": name, "phone": phone, "address": address},
            "payment_method": payment_method["id"],
            "line_items": [
                {
                    "name": item["product"]["name"],
                    "flavor": item["product"]["flavor"],
                    "quantity": item["quantity"],
                    "price": item["product"]["price"],
                    "subtotal": item["subtotal"],
                }
                for item in items
            ],
            "total": total,
        }
        with open(ORDERS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(order) + "\n")

        session["cart"] = {}

        return render_template(
            "order_confirmation.html",
            order=order,
            payment_method=payment_method,
            currency="LYD",
        )

    return render_template(
        "checkout.html",
        items=items,
        total=total,
        currency="LYD",
        payment_methods=PAYMENT_METHODS,
        errors=[],
        form={},
    )


@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        payment_method = PAYMENT_METHODS_BY_ID.get(request.form.get("payment_method"))

        errors = []
        if not name:
            errors.append("Name is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not payment_method or not payment_method["available"]:
            errors.append("Please select a valid payment method.")

        if errors:
            return render_template(
                "subscribe.html",
                plan=SUBSCRIPTION_PLAN,
                payment_methods=PAYMENT_METHODS,
                currency="LYD",
                errors=errors,
                form=request.form,
            )

        subscription = {
            "subscription_id": uuid.uuid4().hex[:8].upper(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "customer": {"name": name, "phone": phone},
            "payment_method": payment_method["id"],
            "plan": SUBSCRIPTION_PLAN["name"],
            "price": SUBSCRIPTION_PLAN["price"],
        }
        with open(SUBSCRIPTIONS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(subscription) + "\n")

        return render_template(
            "subscription_confirmation.html",
            subscription=subscription,
            payment_method=payment_method,
            plan=SUBSCRIPTION_PLAN,
            currency="LYD",
        )

    return render_template(
        "subscribe.html",
        plan=SUBSCRIPTION_PLAN,
        payment_methods=PAYMENT_METHODS,
        currency="LYD",
        errors=[],
        form={},
    )


if __name__ == "__main__":
    app.run(debug=True)
