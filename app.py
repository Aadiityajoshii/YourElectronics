from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv  # ← ADD THIS
import os
import razorpay
import hmac
import hashlib

load_dotenv()  # ← ADD THIS — reads your .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')  # ← CHANGE THIS LINE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electronixs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
razorpay_client = razorpay.Client(
    auth=(os.environ.get('RAZORPAY_KEY_ID'),
          os.environ.get('RAZORPAY_KEY_SECRET'))
)
# ─────────────────────────────────────────
# DATABASE MODELS
# ─────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    discount = db.Column(db.Integer)
    rating = db.Column(db.Float, default=4.5)
    reviews = db.Column(db.Integer, default=0)
    emi = db.Column(db.Integer)
    badge = db.Column(db.String(50))
    image_url = db.Column(db.String(300))
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=100)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────

def seed_products():
    if Product.query.count() > 0:
        return
    products = [
        Product(name='iPhone 15 Pro Max 256GB', brand='Apple', category='Smartphones',
                price=159900, old_price=174900, discount=9, rating=4.8, reviews=12458,
                emi=4886, badge='Top Seller',
                image_url='https://m.media-amazon.com/images/I/81Os1SDWpcL._AC_UF1000,1000_QL80_.jpg',
                description='The most powerful iPhone ever.'),
        Product(name='Samsung Galaxy S24 Ultra 512GB', brand='Samsung', category='Smartphones',
                price=129999, old_price=149999, discount=13, rating=4.7, reviews=8732,
                emi=3970, badge='Best Seller',
                image_url='https://in.static.webuy.com/product_images/Phones/Phones%20Android/SSAMS928B512GTVUNLC_l.jpg',
                description='Galaxy AI with built-in S Pen.'),
        Product(name='OnePlus 12 16GB+512GB', brand='OnePlus', category='Smartphones',
                price=64999, old_price=72999, discount=11, rating=4.6, reviews=5421,
                emi=1987, badge=None,
                image_url='https://rukmini1.flixcart.com/image/1500/1500/xif0q/mobile/7/z/j/12-cph2573-oneplus-original-imahjngudb3jjkew.jpeg?q=70',
                description='Hasselblad camera, Snapdragon 8 Gen 3.'),
        Product(name='MacBook Air M3 16GB 512GB', brand='Apple', category='Laptops',
                price=134900, old_price=149900, discount=10, rating=4.9, reviews=9867,
                emi=4117, badge='Editor Choice',
                image_url='https://ipowerresale.com/cdn/shop/files/media_f720ee06-87b8-47ac-bc83-3fa1a4fe4f32.png?v=1766098580',
                description='Supercharged by M3 chip.'),
        Product(name='Dell XPS 15 9530 i9 RTX 4060', brand='Dell', category='Laptops',
                price=189900, old_price=209900, discount=10, rating=4.7, reviews=3241,
                emi=5797, badge=None,
                image_url='https://microless.com/cdn/products/5a7c8a189c7bed1cf0337d48c373b001-hi.jpg',
                description='Ultimate performance laptop.'),
        Product(name='ASUS ROG Zephyrus G14', brand='ASUS', category='Laptops',
                price=109990, old_price=129990, discount=15, rating=4.6, reviews=4123,
                emi=3356, badge='Gaming Beast',
                image_url='https://dlcdnwebimgs.asus.com/gain/7583764C-92E3-413D-A5AD-4CB7D9713802/w1000/h732',
                description='AMD Ryzen 9 gaming powerhouse.'),
        Product(name='Sony WH-1000XM5 Wireless ANC', brand='Sony', category='Audio',
                price=26990, old_price=34990, discount=23, rating=4.9, reviews=21034,
                emi=824, badge='Best ANC',
                image_url='https://www.sony.co.in/image/6145c1d32e6ac8e63a46c912dc33c5bb?fmt=png-alpha&wid=330',
                description='Industry-leading noise cancellation.'),
        Product(name='Bose QuietComfort 45', brand='Bose', category='Audio',
                price=24990, old_price=32000, discount=22, rating=4.7, reviews=7890,
                emi=763, badge=None,
                image_url='https://media.tatacroma.com/Croma%20Assets/Communication/Headphones%20and%20Earphones/Images/250473_0_kilfds.png',
                description='Legendary Bose noise cancelling.'),
        Product(name='JBL Flip 6 Portable Speaker', brand='JBL', category='Audio',
                price=9999, old_price=13499, discount=26, rating=4.5, reviews=15032,
                emi=305, badge=None,
                image_url='https://in.jbl.com/dw/image/v2/BFND_PRD/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw593abf39/2_JBL_FLIP6_3_4_RIGHT_BLACK_30195_x1.png?sw=535&sh=535',
                description='Powerful sound, waterproof design.'),
        Product(name='Apple Watch Series 9 GPS 45mm', brand='Apple', category='Wearables',
                price=41900, old_price=45900, discount=9, rating=4.8, reviews=6754,
                emi=1279, badge='New',
                image_url='https://img-prd-pim.poorvika.com/product/apple-watch-series-9-gps-45mm-mr973hn-a-left-view.png',
                description='The smartwatch that keeps you healthy.'),
        Product(name='Samsung Galaxy Watch 6 Classic 47mm', brand='Samsung', category='Wearables',
                price=36999, old_price=44999, discount=18, rating=4.6, reviews=4321,
                emi=1130, badge=None,
                image_url='https://www.anmolmobiles.com/cdn/shop/files/71hg6m6m50L._SL1500_-removebg-preview_1.png?v=1764920535',
                description='Classic design meets smartwatch intelligence.'),
        Product(name='PlayStation 5 Disc Edition', brand='Sony', category='Gaming',
                price=54990, old_price=59990, discount=8, rating=4.9, reviews=18901,
                emi=1679, badge='Hot 🔥',
                image_url='https://sgp1.digitaloceanspaces.com/relay-bl-in-records/GameNation/EA_4268',
                description='Experience lightning-fast loading.'),
                # TVs
        Product(name='Samsung 65" 4K QLED Smart TV', brand='Samsung', category='TVs',
                price=89990, old_price=129990, discount=31, stock=25,
                image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f4834b?w=500',
                description='65 inch 4K QLED display with Quantum HDR, built-in Alexa, 120Hz refresh rate.',
                badge='Best Seller', rating=4.6, reviews=1240),

        Product(name='LG 55" OLED C3 4K Smart TV', brand='LG', category='TVs',
                price=129990, old_price=169990, discount=24, stock=15,
                image_url='https://images.unsplash.com/photo-1461151304267-38535e780c79?w=500',
                description='55 inch OLED with perfect blacks, Dolby Vision IQ, G-Sync compatible for gaming.',
                badge='Premium', rating=4.8, reviews=890),

        Product(name='Sony Bravia 50" 4K LED Google TV', brand='Sony', category='TVs',
                price=64990, old_price=84990, discount=24, stock=30,
                image_url='https://images.unsplash.com/photo-1509281373149-e957c6296406?w=500',
                description='50 inch 4K LED with Google TV, Dolby Atmos, X-Reality PRO picture engine.',
                badge='New', rating=4.5, reviews=670),

        # Washing Machines
        Product(name='LG 8Kg Front Load Washing Machine', brand='LG', category='Washing Machines',
                price=54990, old_price=72990, discount=25, stock=20,
                image_url='https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=500',
                description='8Kg front load with AI DD technology, Steam wash, 5 star energy rating.',
                badge='Top Rated', rating=4.7, reviews=2100),

        Product(name='Samsung 7Kg Fully Automatic Top Load', brand='Samsung', category='Washing Machines',
                price=28990, old_price=38990, discount=26, stock=35,
                image_url='https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=500',
                description='7Kg top load with Eco Tub Clean, Digital Inverter Motor, 5 wash programs.',
                badge='Value Pick', rating=4.4, reviews=1560),

        Product(name='Bosch 9Kg Front Load Washing Machine', brand='Bosch', category='Washing Machines',
                price=68990, old_price=89990, discount=23, stock=12,
                image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500',
                description='9Kg front load with EcoSilence Drive, ActiveWater Plus, Anti-vibration design.',
                badge='Premium', rating=4.8, reviews=980),

        # Refrigerators
        Product(name='Samsung 653L French Door Refrigerator', brand='Samsung', category='Refrigerators',
                price=119990, old_price=159990, discount=25, stock=10,
                image_url='https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=500',
                description='653L French door with Twin Cooling Plus, Family Hub display, Wi-Fi enabled.',
                badge='Smart Home', rating=4.6, reviews=540),

        Product(name='LG 471L Double Door Refrigerator', brand='LG', category='Refrigerators',
                price=54990, old_price=71990, discount=24, stock=22,
                image_url='https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=500',
                description='471L double door with Inverter Linear Compressor, Door Cooling+, 10 year warranty.',
                badge='Best Seller', rating=4.7, reviews=1890),

        Product(name='Whirlpool 340L Double Door Refrigerator', brand='Whirlpool', category='Refrigerators',
                price=36990, old_price=47990, discount=23, stock=28,
                image_url='https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500',
                description='340L with Intellisense Inverter, 6th Sense Technology, Microblock anti-bacterial.',
                badge='Value Pick', rating=4.5, reviews=1230),

        # Air Conditioners
        Product(name='Daikin 1.5 Ton 5 Star Split AC', brand='Daikin', category='Air Conditioners',
                price=44990, old_price=58990, discount=24, stock=18,
                image_url='https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500',
                description='1.5 Ton inverter split AC with PM 2.5 filter, Coanda airflow, 5 star rating.',
                badge='Top Rated', rating=4.7, reviews=3200),

        Product(name='Voltas 1.5 Ton 3 Star Window AC', brand='Voltas', category='Air Conditioners',
                price=29990, old_price=39990, discount=25, stock=25,
                image_url='https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=500',
                description='1.5 Ton window AC with auto restart, sleep mode, dust filter, turbo cool.',
                badge='Budget Pick', rating=4.3, reviews=1870),

        Product(name='Blue Star 2 Ton 5 Star Inverter Split AC', brand='Blue Star', category='Air Conditioners',
                price=58990, old_price=75990, discount=22, stock=14,
                image_url='https://images.unsplash.com/photo-1587293852726-70cdb56c2866?w=500',
                description='2 Ton 5 star inverter with self-cleaning, Wi-Fi control, precision cooling.',
                badge='Premium', rating=4.6, reviews=760),

        # Microwaves
        Product(name='Samsung 28L Convection Microwave', brand='Samsung', category='Microwaves',
                price=14990, old_price=19990, discount=25, stock=40,
                image_url='https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=500',
                description='28L convection microwave with SlimFry, ceramic enamel cavity, 900W power.',
                badge='Best Seller', rating=4.5, reviews=2340),

        Product(name='LG 32L All-in-One Charcoal Microwave', brand='LG', category='Microwaves',
                price=22990, old_price=29990, discount=23, stock=20,
                image_url='https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500',
                description='32L with Diet Fry, charcoal lighting heater, Indian roti basket included.',
                badge='New', rating=4.6, reviews=890),
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()
    print("✅ Products seeded!")
# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

def product_to_dict(p):
    return {
        'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category,
        'price': p.price, 'old_price': p.old_price, 'discount': p.discount,
        'rating': p.rating, 'reviews': p.reviews, 'emi': p.emi,
        'badge': p.badge, 'image_url': p.image_url, 'description': p.description
    }

@app.route('/')
def index():
    products = [product_to_dict(p) for p in Product.query.all()]
    cart_count = get_cart_count()
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Welcome back, ' + user.name + '!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.name
        flash('Account created! Welcome to Your Electronixs!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'login_required'}), 401
    existing = CartItem.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if existing:
        existing.quantity += 1
    else:
        item = CartItem(user_id=session['user_id'], product_id=product_id)
        db.session.add(item)
    db.session.commit()
    count = get_cart_count()
    return jsonify({'success': True, 'cart_count': count})

@app.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == session.get('user_id'):
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    items = CartItem.query.filter_by(user_id=session['user_id']).all()
    if not items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))
    total = sum(item.product.price * item.quantity for item in items)
    if request.method == 'GET':
        return render_template('checkout.html', items=items, total=total)
    # POST — save address in session, go to payment
    session['shipping_address'] = {
        'full_name': request.form.get('full_name'),
        'phone':     request.form.get('phone'),
        'address1':  request.form.get('address1'),
        'city':      request.form.get('city'),
        'state':     request.form.get('state'),
        'pincode':   request.form.get('pincode'),
    }
    return redirect(url_for('create_payment'))

@app.route('/create-payment')
def create_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.product.price * item.quantity for item in items)
    # Razorpay amount is in paise (rupees × 100)
    rz_order = razorpay_client.order.create({
        'amount': int(total * 100),
        'currency': 'INR',
        'payment_capture': 1
    })
    return render_template('payment.html',
                           rz_order=rz_order,
                           total=total,
                           razorpay_key=os.environ.get('RAZORPAY_KEY_ID'),
                           user_name=session.get('user_name', ''))

@app.route('/payment-success', methods=['POST'])
def payment_success():
    # Verify payment signature
    payment_id  = request.form.get('razorpay_payment_id')
    order_id    = request.form.get('razorpay_order_id')
    signature   = request.form.get('razorpay_signature')
    key_secret  = os.environ.get('RAZORPAY_KEY_SECRET').encode()
    msg         = (order_id + '|' + payment_id).encode()
    generated   = hmac.new(key_secret, msg, hashlib.sha256).hexdigest()
    if generated != signature:
        flash('❌ Payment verification failed!', 'error')
        return redirect(url_for('cart'))
    # Payment verified — save order, clear cart
    items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.product.price * item.quantity for item in items)
    addr  = session.get('shipping_address', {})
    full_address = f"{addr.get('full_name')}, {addr.get('phone')}, {addr.get('address1')}, {addr.get('city')}, {addr.get('state')} - {addr.get('pincode')}"
    order = Order(
        user_id=session['user_id'],
        total=total,
        status='Confirmed'
    )
    db.session.add(order)
    for item in items:
        item.product.stock -= item.quantity
        db.session.delete(item)
    db.session.commit()
    session.pop('shipping_address', None)
    flash(f'🎉 Order #{order.id} confirmed! Payment ID: {payment_id}', 'success')
    return redirect(url_for('order_history'))

@app.route('/payment-failed')
def payment_failed():
    flash('❌ Payment was cancelled or failed. Try again.', 'error')
    return redirect(url_for('cart'))
@app.route('/orders')
def order_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    orders = Order.query.filter_by(
        user_id=session['user_id']
    ).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=orders)

@app.route('/api/products')
def api_products():
    category = request.args.get('category', 'All')
    search = request.args.get('search', '')
    q = Product.query
    if category != 'All':
        q = q.filter_by(category=category)
    if search:
        q = q.filter(Product.name.ilike(f'%{search}%') | Product.brand.ilike(f'%{search}%'))
    products = q.all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category,
        'price': p.price, 'old_price': p.old_price, 'discount': p.discount,
        'rating': p.rating, 'reviews': p.reviews, 'emi': p.emi, 'badge': p.badge,
        'image_url': p.image_url, 'description': p.description, 'stock': p.stock
    } for p in products])
@app.route('/update-cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    action = request.form.get('action')  # 'increase' or 'decrease'
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
        else:
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('cart'))
    db.session.commit()
    return redirect(url_for('cart'))
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category == product.category,
        Product.id != product_id
    ).limit(4).all()
    cart_count = get_cart_count()
    return render_template('product_detail.html', product=product, related=related, cart_count=cart_count)

def get_cart_count():
    if 'user_id' not in session:
        return 0
    return CartItem.query.filter_by(user_id=session['user_id']).count()

# ─────────────────────────────────────────
# INIT & RUN
# ─────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products()
    app.run(debug=True)
