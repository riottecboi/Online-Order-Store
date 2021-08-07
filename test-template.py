from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "hello"

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/product-details")
def details():
    return render_template("product-details.html")

if __name__ == "__main__":
    app.run()