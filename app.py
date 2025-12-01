import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'store.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

db = SQLAlchemy(app)

# --- Models ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=True) 

    def to_dict(self):
        return {'id': self.id, 'section': self.section, 'sub': self.subcategory, 'title': self.title, 'price': self.price, 'desc': self.description, 'image': self.image_url}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # Storing Address as a JSON String
    address_json = db.Column(db.Text, nullable=True) 

    def to_dict(self):
        return {
            'first_name': self.first_name, 'middle_name': self.middle_name, 
            'last_name': self.last_name, 'phone': self.phone, 
            'email': self.email, 'address': self.address_json
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False) 
    payment_method = db.Column(db.String(50), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_details = db.Column(db.Text, nullable=False) 
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'total': self.total_price, 'items': self.order_details, 'date': self.date_created.strftime("%Y-%m-%d"), 'status': 'Processing'}

# --- Seeding ---
def seed_database():
    if not Product.query.first():
        sample_products = [
            {'id': 101, 'section': 'men', 'sub': 'shirts', 'title': 'Men Classic Shirt', 'price': 1199, 'desc': 'Cotton formal shirt, S–XXL', 'img': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=80'},
            {'id': 102, 'section': 'men', 'sub': 'pants', 'title': 'Men Chinos', 'price': 1499, 'desc': 'Slim-fit chino pants', 'img': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&q=80'},
            {'id': 103, 'section': 'men', 'sub': 'shirts', 'title': 'Men Casual Shirt', 'price': 999, 'desc': 'Checks casual shirt', 'img': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&q=80'},
            {'id': 201, 'section': 'women', 'sub': 'dress', 'title': 'Floral Midi Dress', 'price': 2599, 'desc': 'Lightweight summer dress', 'img': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500&q=80'},
            {'id': 202, 'section': 'women', 'sub': 'saree', 'title': 'Silk Saree', 'price': 4999, 'desc': 'Elegant silk saree with border', 'img': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80'},
            {'id': 203, 'section': 'women', 'sub': 'tops', 'title': 'Lace Top', 'price': 899, 'desc': 'Delicate lace top', 'img': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=500&q=80'},
            {'id': 301, 'section': 'kids', 'sub': 'tshirts', 'title': 'Kids Graphic Tee', 'price': 399, 'desc': '100% cotton tee', 'img': 'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=500&q=80'},
            {'id': 302, 'section': 'kids', 'sub': 'shorts', 'title': 'Kids Denim Shorts', 'price': 499, 'desc': 'Comfort denim shorts', 'img': 'https://images.unsplash.com/photo-1519457431-44ccd64a579b?w=500&q=80'},
            {'id': 303, 'section': 'kids', 'sub': 'tshirts', 'title': 'Kids Polo', 'price': 449, 'desc': 'Smart polo shirt', 'img': 'https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=500&q=80'}
        ]
        for p in sample_products:
            db.session.add(Product(id=p['id'], section=p['section'], subcategory=p['sub'], title=p['title'], price=p['price'], description=p['desc'], image_url=p['img']))
        print("Products seeded.")
    db.session.commit()

# --- Routes ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/products')
def get_products():
    section = request.args.get('section', 'all')
    search = request.args.get('search', '').lower()
    sort_order = request.args.get('sort', 'default')
    query = Product.query
    if section != 'all': query = query.filter_by(section=section)
    if search: query = query.filter((Product.title.ilike(f'%{search}%')) | (Product.description.ilike(f'%{search}%')))
    products = query.all()
    results = [p.to_dict() for p in products]
    if sort_order == 'price-asc': results.sort(key=lambda x: x['price'])
    elif sort_order == 'price-desc': results.sort(key=lambda x: x['price'], reverse=True)
    return jsonify(results)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data.get('email')).first(): return jsonify({'error': 'Email exists'}), 400
    db.session.add(User(first_name=data.get('first_name'), last_name=data.get('last_name'), phone=data.get('phone'), email=data.get('email'), password_hash=generate_password_hash(data.get('password'))))
    db.session.commit()
    return jsonify({'message': 'Registered'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password_hash, data.get('password')):
        return jsonify({'message': 'Success', 'email': user.email, 'name': user.first_name})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user/profile', methods=['GET', 'POST'])
def profile():
    email = request.args.get('email') if request.method == 'GET' else request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user: return jsonify({'error': 'Not found'}), 404
    
    if request.method == 'POST':
        user.address_json = request.json.get('address') # Storing JSON string
        db.session.commit()
        return jsonify({'message': 'Address updated'})
    
    return jsonify(user.to_dict())

@app.route('/api/user/orders')
def get_orders():
    orders = Order.query.filter_by(user_email=request.args.get('email')).order_by(Order.date_created.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    cart = data.get('cart', {})
    if not cart: return jsonify({'error': 'Empty cart'}), 400
    
    total = sum([Product.query.get(pid).price * qty for pid, qty in cart.items() if Product.query.get(pid)])
    details = [f"{Product.query.get(pid).title} (x{qty})" for pid, qty in cart.items() if Product.query.get(pid)]
    
    new_order = Order(
        customer_name=data.get('name'), 
        user_email=data.get('email'), 
        total_price=total, 
        order_details=json.dumps(details),
        shipping_address=data.get('address'),
        payment_method=data.get('payment_method')
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order placed', 'order_id': new_order.id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5000)