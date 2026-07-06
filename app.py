from flask import Flask, render_template

app = Flask(__name__)

SERVICES = [
    {
        "title": "Consulting",
        "description": "Strategic guidance to help your business make the right calls.",
    },
    {
        "title": "Design",
        "description": "Clean, modern design that puts your brand front and center.",
    },
    {
        "title": "Development",
        "description": "Reliable, well-built software tailored to your needs.",
    },
]


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


if __name__ == "__main__":
    app.run(debug=True)
