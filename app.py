import os

from flask import Flask, render_template

app = Flask(__name__)

PRODUCT_IMAGE_DIR = os.path.join(app.static_folder, "images", "products")

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
    {"name": "Whey HD", "flavor": "Chocolate Cookie", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-chocolate-cookie.jpg"},
    {"name": "Whey HD", "flavor": "Strawberry Cake", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-strawberry-cake.jpg"},
    {"name": "Whey HD", "flavor": "Milk and Cookies", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-milk-and-cookies.jpg"},
    {"name": "Whey HD", "flavor": "Blueberry Muffin", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-blueberry-muffin.jpg"},
    {"name": "Whey HD", "flavor": "Salted Caramel", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery", "image": "whey-hd-salted-caramel.jpg"},
    {"name": "ISO HD", "flavor": "Cookies and Cream", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery", "image": "iso-hd-cookies-and-cream.jpg"},
    {"name": "ISO HD", "flavor": "Chocolate Brownie", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery", "image": "iso-hd-chocolate-brownie.jpg"},
    {"name": "Micronized Creatine", "flavor": "Unflavored", "size": "1.32 lbs (600g)", "price": 370, "category": "Protein & Recovery", "image": "micronized-creatine-unflavored.jpg"},
    {"name": "Best BCAA", "flavor": "Fruit Punch", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy", "image": "best-bcaa-fruit-punch.jpg"},
    {"name": "Best BCAA", "flavor": "Watermelon Ice", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy", "image": "best-bcaa-watermelon-ice.jpg"},
    {"name": "1.M.R The OG Formula", "flavor": "Fruit Punch", "size": "12.1 oz (342.5g)", "price": 340, "category": "Pre-Workout & Energy", "image": "1mr-og-fruit-punch.jpg"},
    {"name": "1.M.R The OG Formula", "flavor": "Sour Gummy", "size": "12.2 oz (346g)", "price": 340, "category": "Pre-Workout & Energy", "image": "1mr-og-sour-gummy.jpg"},
    {"name": "CLA + Carnitine", "flavor": "Snow Cone", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness", "image": "cla-carnitine-snow-cone.jpg"},
    {"name": "CLA + Carnitine", "flavor": "Rainbow Ice", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness", "image": "cla-carnitine-rainbow-ice.jpg"},
    {"name": "RoxyLean", "flavor": "Fat Burner & Thermogenic", "size": "60 capsules", "price": 290, "category": "Vitamins & Wellness", "image": "roxylean.jpg"},
]


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


def product_image_url(product):
    if os.path.exists(os.path.join(PRODUCT_IMAGE_DIR, product["image"])):
        return f"images/products/{product['image']}"
    return None


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


if __name__ == "__main__":
    app.run(debug=True)
