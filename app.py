import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, abort, redirect, render_template, request, session, url_for

from translations import t as translate

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

PRODUCT_IMAGE_DIR = os.path.join(app.static_folder, "images", "products")
ORDERS_LOG_PATH = os.path.join(os.path.dirname(__file__), "orders.jsonl")
SUBSCRIPTIONS_LOG_PATH = os.path.join(os.path.dirname(__file__), "subscriptions.jsonl")

SUBSCRIPTION_PLAN = {"id": "full-coaching-plan", "price": 120, "feature_keys": [
    "plan.feature.1", "plan.feature.2", "plan.feature.3", "plan.feature.4",
]}

CATEGORIES = ["protein-recovery", "pre-workout-energy", "vitamins-wellness"]

PRODUCTS = [
    {"id": 1, "name": "Whey HD", "flavor": "Chocolate Cookie", "size": "4.07 lbs", "price": 520, "category": "protein-recovery", "image": "whey-hd-chocolate-cookie.jpg"},
    {"id": 2, "name": "Whey HD", "flavor": "Strawberry Cake", "size": "4.1 lbs", "price": 520, "category": "protein-recovery", "image": "whey-hd-strawberry-cake.jpg"},
    {"id": 3, "name": "Whey HD", "flavor": "Milk and Cookies", "size": "4.1 lbs", "price": 520, "category": "protein-recovery", "image": "whey-hd-milk-and-cookies.jpg"},
    {"id": 4, "name": "Whey HD", "flavor": "Blueberry Muffin", "size": "4.07 lbs", "price": 520, "category": "protein-recovery", "image": "whey-hd-blueberry-muffin.jpg"},
    {"id": 5, "name": "Whey HD", "flavor": "Salted Caramel", "size": "4.07 lbs", "price": 520, "category": "protein-recovery", "image": "whey-hd-salted-caramel.jpg"},
    {"id": 6, "name": "ISO HD", "flavor": "Cookies and Cream", "size": "4.9 lbs", "price": 580, "category": "protein-recovery", "image": "iso-hd-cookies-and-cream.jpg"},
    {"id": 7, "name": "ISO HD", "flavor": "Chocolate Brownie", "size": "4.9 lbs", "price": 580, "category": "protein-recovery", "image": "iso-hd-chocolate-brownie.jpg"},
    {"id": 8, "name": "Micronized Creatine", "flavor": "Unflavored", "size": "1.32 lbs (600g)", "price": 370, "category": "protein-recovery", "image": "micronized-creatine-unflavored.webp"},
    {"id": 9, "name": "Best BCAA", "flavor": "Fruit Punch", "size": "10.58 oz (300g)", "price": 290, "category": "pre-workout-energy", "image": "best-bcaa-fruit-punch.webp"},
    {"id": 10, "name": "Best BCAA", "flavor": "Watermelon Ice", "size": "10.58 oz (300g)", "price": 290, "category": "pre-workout-energy", "image": "best-bcaa-watermelon-ice.webp"},
    {"id": 11, "name": "1.M.R The OG Formula", "flavor": "Fruit Punch", "size": "12.1 oz (342.5g)", "price": 340, "category": "pre-workout-energy", "image": "1mr-og-fruit-punch.webp"},
    {"id": 12, "name": "1.M.R The OG Formula", "flavor": "Sour Gummy", "size": "12.2 oz (346g)", "price": 340, "category": "pre-workout-energy", "image": "1mr-og-sour-gummy.webp"},
    {"id": 13, "name": "CLA + Carnitine", "flavor": "Snow Cone", "size": "12.34 oz (350g)", "price": 290, "category": "vitamins-wellness", "image": "cla-carnitine-snow-cone.jpg"},
    {"id": 14, "name": "CLA + Carnitine", "flavor": "Rainbow Ice", "size": "12.34 oz (350g)", "price": 290, "category": "vitamins-wellness", "image": "cla-carnitine-rainbow-ice.webp"},
    {"id": 15, "name": "RoxyLean", "flavor": "Fat Burner & Thermogenic", "size": "60 capsules", "price": 290, "category": "vitamins-wellness", "image": "roxylean.webp"},
]
PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

# Supplement sets keyed by recommendation set id (goals map to one of these below)
CALCULATOR_RECOMMENDATION_SETS = {
    "muscle": [
        {"product_id": 1, "timing_key": "calculators.timing.whey"},
        {"product_id": 8, "timing_key": "calculators.timing.creatine"},
    ],
    "cut": [
        {"product_id": 6, "timing_key": "calculators.timing.whey"},
        {"product_id": 14, "timing_key": "calculators.timing.carnitine"},
    ],
    "performance": [
        {"product_id": 8, "timing_key": "calculators.timing.creatine"},
        {"product_id": 11, "timing_key": "calculators.timing.pre_workout"},
    ],
}

# Calculator goal -> recommendation set (weight loss and cutting share the same stack)
CALCULATOR_GOAL_TO_SET = {
    "muscle": "muscle",
    "lose": "cut",
    "cut": "cut",
    "performance": "performance",
}

# Protein target range (g per kg bodyweight) used by the supplement calculator, per goal
CALCULATOR_PROTEIN_PER_KG = {
    "muscle": 2.2,
    "lose": 1.8,
    "cut": 2.0,
    "performance": 1.6,
}

PAYMENT_METHODS = [
    {"id": "cod", "available": True},
    {"id": "bank_transfer", "available": True},
    {"id": "card", "available": False},
    {"id": "mobile_wallet", "available": False},
]
PAYMENT_METHODS_BY_ID = {m["id"]: m for m in PAYMENT_METHODS}


def get_lang():
    return session.get("lang", "en")


@app.context_processor
def inject_i18n():
    lang = get_lang()
    return {
        "lang": lang,
        "text_dir": "rtl" if lang == "ar" else "ltr",
        "t": lambda key, **kwargs: translate(key, lang=lang, **kwargs),
    }


@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ("en", "ar"):
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("index"))


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


@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES, plan=SUBSCRIPTION_PLAN, currency="LYD")


@app.route("/products")
def products():
    grouped = [
        {
            "slug": category,
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
    lang = get_lang()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        address = (request.form.get("address") or "").strip()
        payment_method = PAYMENT_METHODS_BY_ID.get(request.form.get("payment_method"))

        errors = []
        if not name:
            errors.append(translate("error.name_required", lang=lang))
        if not phone:
            errors.append(translate("error.phone_required", lang=lang))
        if not address:
            errors.append(translate("error.address_required", lang=lang))
        if not payment_method or not payment_method["available"]:
            errors.append(translate("error.payment_method_invalid", lang=lang))

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
    lang = get_lang()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        payment_method = PAYMENT_METHODS_BY_ID.get(request.form.get("payment_method"))

        errors = []
        if not name:
            errors.append(translate("error.name_required", lang=lang))
        if not phone:
            errors.append(translate("error.phone_required", lang=lang))
        if not payment_method or not payment_method["available"]:
            errors.append(translate("error.payment_method_invalid", lang=lang))

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
            "plan": SUBSCRIPTION_PLAN["id"],
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


@app.route("/calculators")
def calculators():
    recommendation_sets = {}
    for goal, set_id in CALCULATOR_GOAL_TO_SET.items():
        items = []
        for entry in CALCULATOR_RECOMMENDATION_SETS[set_id]:
            product = PRODUCTS_BY_ID[entry["product_id"]]
            items.append(
                {
                    "product": product,
                    "image_path": product_image_url(product),
                    "timing_key": entry["timing_key"],
                }
            )
        recommendation_sets[goal] = items

    return render_template(
        "calculators.html",
        recommendation_sets=recommendation_sets,
        protein_per_kg=CALCULATOR_PROTEIN_PER_KG,
        currency="LYD",
    )


if __name__ == "__main__":
    app.run(debug=True)
