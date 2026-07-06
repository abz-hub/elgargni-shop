from flask import Flask, render_template

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


if __name__ == "__main__":
    app.run(debug=True)
