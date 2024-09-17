from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:cafeteria@localhost/duka'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Product model (table)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

# Define the Sale model (table)
class Sale(db.Model):
    __tablename__ = 'sales'
    sid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))

# Create the tables
with app.app_context():
    db.create_all()

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for adding and viewing products
@app.route('/products', methods=["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form["product_name"]
        bp = request.form["B_P"]
        sp = request.form["S_P"]
        quantity = request.form["quantity"]

        # Insert new product
        new_product = Product(name=name, buying_price=bp, selling_price=sp, stock_quantity=quantity)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products'))

    # Query all products from the database
    products = Product.query.all()

    # Pass the products to the template
    return render_template('products.html', rows=products)


# Route to display and handle adding sales
@app.route('/sales', methods=["GET", "POST"])
def sales():
    if request.method == "POST":
        # Get form data
        pid = request.form.get("pid")
        quantity = request.form.get("quantity")

        # Validate that the product ID and quantity are not empty
        if not pid or not quantity:
            return "Product and quantity are required", 400

        try:
            pid = int(pid)  # Ensure pid is an integer
            quantity = int(quantity)  # Ensure quantity is an integer
        except ValueError:
            return "Invalid product or quantity", 400

        # Check product stock before proceeding
        product = Product.query.get(pid)
        if product and quantity <= product.stock_quantity:
            # Deduct the quantity from the product's stock
            product.stock_quantity -= quantity
            new_sale = Sale(pid=pid, quantity=quantity)
            db.session.add(new_sale)
            db.session.commit()
        else:
            # Handle insufficient stock or invalid product scenario
            return "Insufficient stock or invalid product", 400

        return redirect(url_for('sales'))

    # Get sales data for display
    sales_data = db.session.query(Sale.sid, Product.name, Product.selling_price, Sale.quantity,
                                  (Product.selling_price * Sale.quantity).label('total'), Sale.created_at)\
                           .join(Product, Product.id == Sale.pid).all()
    products = Product.query.all()  # Retrieve products for the sale form dropdown
    return render_template('sales.html', b=sales_data, products=products)


# Route to display dashboard data
@app.route('/dashboard')
def dashboard():
    sales_data = db.session.query(db.func.sum(Product.selling_price * Sale.quantity).label('total_sales'),
                                  Product.name).join(Sale, Product.id == Sale.pid)\
                              .group_by(Product.id).all()

    labels = [item.name for item in sales_data]
    data = [item.total_sales for item in sales_data]
    colours = ["#3cba9f"] * len(labels)

    return render_template('dashboard.html', label=labels, data=data, colours=colours)

if __name__ == "__main__":
    app.run(debug=True)
