from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load products from JSON
def load_products():
    with open('data/products.json', 'r') as f:
        return json.load(f)

@app.route('/')
def home():
    products = load_products()
    query = request.args.get('query', '').lower()
    if query:
        filtered_products = [p for p in products if query in p['name'].lower() or query in p['description'].lower()]
    else:
        filtered_products = products
    return render_template('home.html', products=filtered_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('product.html', product=product)
    else:
        return "Product not found", 404

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product_id)
    session.modified = True
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    products = load_products()
    cart_product_ids = session.get('cart', [])
    cart_items = [p for p in products if p['id'] in cart_product_ids]
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Simulate checkout process
        session.pop('cart', None)
        return redirect(url_for('thank_you'))
    return render_template('checkout.html')

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
