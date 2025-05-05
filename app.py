from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load products from JSON file
def load_products():
    try:
        with open('products.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initial product data if file doesn't exist
        products = {
            "featured": [
                {
                    "id": 1,
                    "name": "Banarasi Silk Saree",
                    "price": 8999,
                    "image": "static/images/products/banarasi-silk.jpg",
                    "description": "Handcrafted Banarasi silk saree with intricate gold zari work",
                    "category": "silk",
                    "color": "red",
                    "rating": 4.8
                },
                {
                    "id": 2,
                    "name": "Kanjivaram Silk Saree",
                    "price": 12999,
                    "image": "static/images/products/kanjivaram.jpg",
                    "description": "Traditional Kanjivaram silk saree with temple border",
                    "category": "silk",
                    "color": "purple",
                    "rating": 4.9
                },
                {
                    "id": 3,
                    "name": "Cotton Handloom Saree",
                    "price": 2999,
                    "image": "static/images/products/cotton-handloom.jpg",
                    "description": "Lightweight cotton handloom saree with contemporary block prints",
                    "category": "cotton", 
                    "color": "blue",
                    "rating": 4.5
                },
                {
                    "id": 4,
                    "name": "Chanderi Silk Saree",
                    "price": 4999,
                    "image": "static/images/products/chanderi.jpg",
                    "description": "Elegant Chanderi silk saree with golden border",
                    "category": "silk",
                    "color": "green",
                    "rating": 4.7
                }
            ],
            "all": [
                # All products including featured ones and more
            ]
        }
        
        # Clone featured products to all products
        products["all"] = products["featured"].copy()
        
        # Add more products to all
        products["all"].extend([
            {
                "id": 5,
                "name": "Tussar Silk Saree",
                "price": 5999,
                "image": "static/images/products/tussar.jpg",
                "description": "Natural Tussar silk saree with hand-painted Madhubani art",
                "category": "silk",
                "color": "beige",
                "rating": 4.6
            },
            {
                "id": 6,
                "name": "Linen Saree",
                "price": 3999,
                "image": "static/images/products/linen.jpg",
                "description": "Premium linen saree with silver zari border",
                "category": "linen",
                "color": "grey",
                "rating": 4.4
            }
        ])
        
        # Save initial products
        with open('products.json', 'w') as f:
            json.dump(products, f, indent=4)
        return products

# Save products to JSON
def save_products(products):
    with open('products.json', 'w') as f:
        json.dump(products, f, indent=4)

# User Database
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        users = {
            "admin@sharee.com": {
                "name": "Admin",
                "password": "admin123",  # In production, use hashed passwords!
                "role": "admin"
            }
        }
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
        return users

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Cart Management
def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

# Routes
@app.route('/')
def home():
    products = load_products()
    
    # Check if products is properly loaded and has the expected structure
    if not products or "featured" not in products:
        # Initialize with an empty list if there's an issue
        featured_products = []
    else:
        featured_products = products["featured"]
    
    return render_template('index.html', featured_products=featured_products)

@app.route('/shop')
def shop():
    products = load_products()
    category = request.args.get('category', '')
    color = request.args.get('color', '')
    sort = request.args.get('sort', '')
    
    filtered_products = products["all"]
    
    # Apply filters
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
    if color:
        filtered_products = [p for p in filtered_products if p["color"] == color]
    
    # Apply sorting
    if sort == 'price_low':
        filtered_products = sorted(filtered_products, key=lambda p: p["price"])
    elif sort == 'price_high':
        filtered_products = sorted(filtered_products, key=lambda p: p["price"], reverse=True)
    elif sort == 'rating':
        filtered_products = sorted(filtered_products, key=lambda p: p["rating"], reverse=True)
    
    return render_template('shop.html', products=filtered_products, 
                          category=category, color=color, sort=sort)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = load_products()
    product = next((p for p in products["all"] if p["id"] == product_id), None)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('shop'))
    
    # Get related products (same category)
    related = [p for p in products["all"] if p["category"] == product["category"] and p["id"] != product_id][:4]
    
    return render_template('product_detail.html', product=product, related_products=related)

@app.route('/cart')
def cart():
    cart_items = get_cart()
    products = load_products()
    
    # Get full product details for cart items
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = next((p for p in products["all"] if p["id"] == item["product_id"]), None)
        if product:
            item_total = product["price"] * item["quantity"]
            cart_products.append({
                "product": product,
                "quantity": item["quantity"],
                "total": item_total
            })
            total += item_total
    
    return render_template('cart.html', cart_products=cart_products, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    
    cart = get_cart()
    
    # Check if product already in cart
    found = False
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            found = True
            break
    
    if not found:
        cart.append({"product_id": product_id, "quantity": quantity})
    
    save_cart(cart)
    flash("Product added to cart!", "success")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success", "cart_count": sum(item["quantity"] for item in cart)})
    else:
        return redirect(request.referrer or url_for('shop'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    cart = get_cart()
    
    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        cart = [item for item in cart if item["product_id"] != product_id]
    else:
        # Update quantity
        for item in cart:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                break
    
    save_cart(cart)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    else:
        return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'user_email' not in session:
        flash("Please login to proceed with checkout", "error")
        session['redirect_after_login'] = url_for('checkout')
        return redirect(url_for('login'))
    
    cart_items = get_cart()
    products = load_products()
    
    # Get full product details for cart items
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = next((p for p in products["all"] if p["id"] == item["product_id"]), None)
        if product:
            item_total = product["price"] * item["quantity"]
            cart_products.append({
                "product": product,
                "quantity": item["quantity"],
                "total": item_total
            })
            total += item_total
    
    return render_template('checkout.html', cart_products=cart_products, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # Process order (would connect to payment gateway in production)
    # For demo, just clear cart and show confirmation
    session.pop('cart', None)
    
    return render_template('order_confirmation.html', 
                          order_id=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        
        if email in users and users[email]["password"] == password:
            session['user_email'] = email
            session['user_name'] = users[email]["name"]
            session['user_role'] = users[email]["role"]
            
            flash(f"Welcome back, {users[email]['name']}!", "success")
            
            # Redirect to saved URL if exists
            redirect_url = session.pop('redirect_after_login', url_for('home'))
            return redirect(redirect_url)
        else:
            flash("Invalid email or password", "error")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        
        if email in users:
            flash("Email already registered", "error")
        else:
            users[email] = {
                "name": name,
                "password": password,  # In production, hash passwords!
                "role": "customer"
            }
            save_users(users)
            
            session['user_email'] = email
            session['user_name'] = name
            session['user_role'] = "customer"
            
            flash("Registration successful!", "success")
            return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash("You have been logged out", "info")
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('home'))
    
    products = load_products()
    users = load_users()
    
    return render_template('admin/dashboard.html', 
                          products=products["all"], 
                          user_count=len(users))

@app.route('/admin/products')
def admin_products():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('home'))
    
    products = load_products()
    
    return render_template('admin/products.html', products=products["all"])

@app.route('/admin/add_product', methods=['GET', 'POST'])
def admin_add_product():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        products = load_products()
        
        # Get next available ID
        next_id = max([p["id"] for p in products["all"]]) + 1 if products["all"] else 1
        
        new_product = {
            "id": next_id,
            "name": request.form.get('name'),
            "price": int(request.form.get('price')),
            "description": request.form.get('description'),
            "category": request.form.get('category'),
            "color": request.form.get('color'),
            "rating": 0,
            "image": "static/images/products/default.jpg"  # Default image
        }
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_product["image"] = file_path
        
        products["all"].append(new_product)
        
        # Add to featured if checked
        if request.form.get('featured') == 'on':
            products["featured"].append(new_product)
        
        save_products(products)
        
        flash("Product added successfully", "success")
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('home'))
    
    products = load_products()
    product = next((p for p in products["all"] if p["id"] == product_id), None)
    
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        # Update product data
        product["name"] = request.form.get('name')
        product["price"] = int(request.form.get('price'))
        product["description"] = request.form.get('description')
        product["category"] = request.form.get('category')
        product["color"] = request.form.get('color')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                product["image"] = file_path
        
        # Update featured status
        is_featured = request.form.get('featured') == 'on'
        featured_ids = [p["id"] for p in products["featured"]]
        
        if is_featured and product_id not in featured_ids:
            products["featured"].append(product)
        elif not is_featured and product_id in featured_ids:
            products["featured"] = [p for p in products["featured"] if p["id"] != product_id]
        
        save_products(products)
        
        flash("Product updated successfully", "success")
        return redirect(url_for('admin_products'))
    
    # Check if product is featured
    is_featured = product_id in [p["id"] for p in products["featured"]]
    
    return render_template('admin/edit_product.html', product=product, is_featured=is_featured)

@app.route('/admin/delete_product/<int:product_id>')
def admin_delete_product(product_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("Access denied", "error")
        return redirect(url_for('home'))
    
    products = load_products()
    
    # Remove from all products
    products["all"] = [p for p in products["all"] if p["id"] != product_id]
    
    # Remove from featured products
    products["featured"] = [p for p in products["featured"] if p["id"] != product_id]
    
    save_products(products)
    
    flash("Product deleted successfully", "success")
    return redirect(url_for('admin_products'))

@app.template_filter('currency')
def currency_filter(value):
    return f"₹{value:,.2f}"

if __name__ == '__main__':
    app.run(debug=True)