from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/product-details")
def details():
    return render_template("product-details.html")

@app.route("/contact")
def contact():
    return render_template("thankyou.html")

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()