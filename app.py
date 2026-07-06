from flask import Flask, render_template

app = Flask(__name__)

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
    {"name": "Whey HD", "flavor": "Chocolate Cookie", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery"},
    {"name": "Whey HD", "flavor": "Strawberry Cake", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery"},
    {"name": "Whey HD", "flavor": "Milk and Cookies", "size": "4.1 lbs", "price": 520, "category": "Protein & Recovery"},
    {"name": "Whey HD", "flavor": "Blueberry Muffin", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery"},
    {"name": "Whey HD", "flavor": "Salted Caramel", "size": "4.07 lbs", "price": 520, "category": "Protein & Recovery"},
    {"name": "ISO HD", "flavor": "Cookies and Cream", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery"},
    {"name": "ISO HD", "flavor": "Chocolate Brownie", "size": "4.9 lbs", "price": 580, "category": "Protein & Recovery"},
    {"name": "Micronized Creatine", "flavor": "Unflavored", "size": "1.32 lbs (600g)", "price": 370, "category": "Protein & Recovery"},
    {"name": "Best BCAA", "flavor": "Fruit Punch", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy"},
    {"name": "Best BCAA", "flavor": "Watermelon Ice", "size": "10.58 oz (300g)", "price": 290, "category": "Pre-Workout & Energy"},
    {"name": "1.M.R The OG Formula", "flavor": "Fruit Punch", "size": "12.1 oz (342.5g)", "price": 340, "category": "Pre-Workout & Energy"},
    {"name": "1.M.R The OG Formula", "flavor": "Sour Gummy", "size": "12.2 oz (346g)", "price": 340, "category": "Pre-Workout & Energy"},
    {"name": "CLA + Carnitine", "flavor": "Snow Cone", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness"},
    {"name": "CLA + Carnitine", "flavor": "Rainbow Ice", "size": "12.34 oz (350g)", "price": 290, "category": "Vitamins & Wellness"},
    {"name": "RoxyLean", "flavor": "Fat Burner & Thermogenic", "size": "60 capsules", "price": 290, "category": "Vitamins & Wellness"},
]


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


@app.route("/products")
def products():
    grouped = [
        {
            "name": category,
            "slug": slugify(category),
            "products": [p for p in PRODUCTS if p["category"] == category],
        }
        for category in CATEGORIES
    ]
    return render_template("products.html", grouped=grouped, currency="LYD")


if __name__ == "__main__":
    app.run(debug=True)
