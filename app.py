import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Load product data from JSON
def load_products():
    with open('data/products.json') as f:
        return json.load(f)

@app.route('/')
def home():
    products = load_products()
    return render_template('home.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return render_template('product.html', product=product)
    return "Product not found", 404

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product_id)
    session.modified = True

    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart_items = []
    if 'cart' in session:
        products = load_products()
        for product_id in session['cart']:
            product = next((p for p in products if p["id"] == product_id), None)
            if product:
                cart_items.append(product)
    return render_template('cart.html', cart=cart_items)

# 🗑️ Add this BELOW /cart and ABOVE main
@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [pid for pid in session['cart'] if pid != product_id]
        session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    cart_items = []
    total_price = 0

    if 'cart' in session:
        products = load_products()
        for product_id in session['cart']:
            product = next((p for p in products if p["id"] == product_id), None)
            if product:
                cart_items.append(product)
                total_price += product["price"]

    return render_template('checkout.html', cart=cart_items, total=total_price)

@app.route('/place-order', methods=['POST'])
def place_order():
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']

    cart_items = []
    total = 0

    if 'cart' in session:
        products = load_products()
        for product_id in session['cart']:
            product = next((p for p in products if p["id"] == product_id), None)
            if product:
                cart_items.append(product)
                total += product["price"]

    # Save order to file
    order_data = {
        "name": name,
        "email": email,
        "address": address,
        "items": cart_items,
        "total": total
    }

    with open('data/orders.json', 'a') as f:
        f.write(json.dumps(order_data) + "\n")

    session.pop('cart', None)
    return render_template("thankyou.html", name=name)


if __name__ == '__main__':
    app.run(debug=True)
    