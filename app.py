import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, CompanySettings, Category, Product, Order, OrderItem, Invoice, InvoiceItem
from seed_data import seed

app = Flask(__name__)
app.secret_key = 'ztech-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'ztech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def generate_order_number():
    date_str = datetime.utcnow().strftime('%Y%m%d')
    suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
    return f'ORD-{date_str}-{suffix}'


def generate_invoice_number():
    date_str = datetime.utcnow().strftime('%Y%m%d')
    suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
    return f'INV-{date_str}-{suffix}'


@app.context_processor
def inject_globals():
    company = CompanySettings.query.first()
    if not company:
        company = CompanySettings(
            name='ZTech Electronics',
            tagline='Your Microcontroller Parts Supplier',
            currency_symbol='₱',
            tax_rate=12.0
        )
    categories = Category.query.order_by(Category.name).all()
    return dict(company=company, categories=categories)


# ── Shop Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    cat_slug = request.args.get('category', '')
    selected_category = None
    if cat_slug:
        selected_category = Category.query.filter_by(slug=cat_slug).first()
        products = Product.query.filter_by(is_active=True, category_id=selected_category.id).all() if selected_category else Product.query.filter_by(is_active=True).all()
    else:
        products = Product.query.filter_by(is_active=True).all()
    return render_template('index.html', products=products, selected_category=selected_category, current_slug=cat_slug)


@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)


@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    items = []
    subtotal = 0.0
    for pid, item in cart_data.items():
        line_sub = item['price'] * item['quantity']
        subtotal += line_sub
        items.append({
            'product_id': pid,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': line_sub,
        })
    company = CompanySettings.query.first()
    tax_rate = company.tax_rate if company else 12.0
    tax = subtotal * (tax_rate / 100)
    total = subtotal + tax
    return render_template('cart.html', items=items, subtotal=subtotal, tax=tax, total=total, tax_rate=tax_rate)


@app.route('/cart/add', methods=['POST'])
def cart_add():
    data = request.get_json()
    product_id = int(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False}), 404
    cart = session.get('cart', {})
    key = str(product_id)
    if key in cart:
        cart[key]['quantity'] += quantity
    else:
        cart[key] = {'name': product.name, 'price': product.price, 'quantity': quantity}
    session['cart'] = cart
    count = sum(i['quantity'] for i in cart.values())
    return jsonify({'success': True, 'count': count})


@app.route('/cart/update', methods=['POST'])
def cart_update():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    cart = session.get('cart', {})
    if product_id in cart:
        if quantity <= 0:
            del cart[product_id]
        else:
            cart[product_id]['quantity'] = quantity
    session['cart'] = cart
    return jsonify({'success': True})


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart
    return jsonify({'success': True})


@app.route('/cart/count')
def cart_count():
    cart = session.get('cart', {})
    count = sum(i['quantity'] for i in cart.values())
    return jsonify({'count': count})


@app.route('/checkout', methods=['GET'])
def checkout():
    cart_data = session.get('cart', {})
    if not cart_data:
        return redirect(url_for('cart'))
    items = []
    subtotal = 0.0
    for pid, item in cart_data.items():
        line_sub = item['price'] * item['quantity']
        subtotal += line_sub
        items.append({'product_id': pid, 'name': item['name'], 'price': item['price'],
                      'quantity': item['quantity'], 'subtotal': line_sub})
    company = CompanySettings.query.first()
    tax_rate = company.tax_rate if company else 12.0
    tax = subtotal * (tax_rate / 100)
    total = subtotal + tax
    return render_template('checkout.html', items=items, subtotal=subtotal, tax=tax, total=total, tax_rate=tax_rate)


@app.route('/checkout', methods=['POST'])
def checkout_post():
    cart_data = session.get('cart', {})
    if not cart_data:
        return redirect(url_for('cart'))

    company = CompanySettings.query.first()
    tax_rate = company.tax_rate if company else 12.0
    subtotal = sum(i['price'] * i['quantity'] for i in cart_data.values())
    tax = subtotal * (tax_rate / 100)
    total = subtotal + tax

    order_number = generate_order_number()
    order = Order(
        order_number=order_number,
        customer_name=request.form.get('customer_name'),
        customer_email=request.form.get('customer_email'),
        customer_phone=request.form.get('customer_phone'),
        shipping_address=request.form.get('shipping_address'),
        city=request.form.get('city'),
        notes=request.form.get('notes'),
        total_amount=total,
        tax_amount=tax,
        status='pending'
    )
    db.session.add(order)
    db.session.flush()

    for pid, item in cart_data.items():
        oi = OrderItem(
            order_id=order.id,
            product_id=int(pid) if pid.isdigit() else None,
            product_name=item['name'],
            unit_price=item['price'],
            quantity=item['quantity'],
            subtotal=item['price'] * item['quantity']
        )
        db.session.add(oi)

    db.session.commit()
    session.pop('cart', None)
    return redirect(url_for('order_success', order_number=order_number))


@app.route('/order-success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_success.html', order=order)


@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=all_orders)


@app.route('/orders/<order_number>')
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_detail.html', order=order)


# ── Invoice Routes ────────────────────────────────────────────────────────────

@app.route('/invoices')
def invoices():
    all_invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoice_builder.html', invoices=all_invoices, mode='list')


@app.route('/invoices/new', methods=['GET'])
def invoice_new():
    return render_template('invoice_builder.html', mode='new', invoices=[])


@app.route('/invoices/new', methods=['POST'])
def invoice_new_post():
    company = CompanySettings.query.first()
    tax_rate = company.tax_rate if company else 12.0

    descriptions = request.form.getlist('item_description[]')
    quantities = request.form.getlist('item_quantity[]')
    unit_prices = request.form.getlist('item_unit_price[]')

    subtotal = 0.0
    line_items = []
    for desc, qty, price in zip(descriptions, quantities, unit_prices):
        if desc.strip():
            q = int(qty) if qty else 1
            p = float(price) if price else 0.0
            sub = q * p
            subtotal += sub
            line_items.append((desc, q, p, sub))

    tax = subtotal * (tax_rate / 100)
    total = subtotal + tax

    inv_number = generate_invoice_number()
    due_date_str = request.form.get('due_date')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

    invoice = Invoice(
        invoice_number=inv_number,
        client_name=request.form.get('client_name'),
        client_email=request.form.get('client_email'),
        client_address=request.form.get('client_address'),
        due_date=due_date,
        notes=request.form.get('notes'),
        subtotal=subtotal,
        tax_amount=tax,
        total_amount=total,
        status='draft'
    )
    db.session.add(invoice)
    db.session.flush()

    for desc, qty, price, sub in line_items:
        ii = InvoiceItem(invoice_id=invoice.id, description=desc, quantity=qty, unit_price=price, subtotal=sub)
        db.session.add(ii)

    db.session.commit()
    return redirect(url_for('invoice_view', invoice_number=inv_number))


@app.route('/invoices/<invoice_number>')
def invoice_view(invoice_number):
    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first_or_404()
    return render_template('invoice_view.html', invoice=invoice)


@app.route('/invoices/<invoice_number>/delete', methods=['POST'])
def invoice_delete(invoice_number):
    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first_or_404()
    InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted successfully.', 'success')
    return redirect(url_for('invoices'))


# ── Settings Routes ───────────────────────────────────────────────────────────

@app.route('/settings', methods=['GET'])
def settings():
    company = CompanySettings.query.first()
    return render_template('settings.html', company=company)


@app.route('/settings', methods=['POST'])
def settings_post():
    company = CompanySettings.query.first()
    if not company:
        company = CompanySettings()
        db.session.add(company)
    company.name = request.form.get('name', company.name)
    company.tagline = request.form.get('tagline', '')
    company.address = request.form.get('address', '')
    company.city = request.form.get('city', '')
    company.phone = request.form.get('phone', '')
    company.email = request.form.get('email', '')
    company.website = request.form.get('website', '')
    company.currency_symbol = request.form.get('currency_symbol', '₱')
    try:
        company.tax_rate = float(request.form.get('tax_rate', 12.0))
    except ValueError:
        company.tax_rate = 12.0
    db.session.commit()
    flash('Settings saved successfully!', 'success')
    return redirect(url_for('settings'))


# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/products')
def api_products():
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    return jsonify([{'id': p.id, 'name': p.name, 'sku': p.sku, 'price': p.price} for p in products])


# ── Bootstrap ─────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    if CompanySettings.query.first() is None:
        seed()

if __name__ == '__main__':
    app.run(debug=True)
