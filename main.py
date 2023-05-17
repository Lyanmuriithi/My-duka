from flask import Flask, render_template,request,redirect

import psycopg2

app = Flask(__name__)

conn=psycopg2.connect("host='localhost' user='postgres' password='cafeteria' dbname='myduka'")

 
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/products', methods=["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form["product_name"]
        bp = request.form["B_P"]
        sp = request.form["S_P"]
        quantity = request.form["quantity"]
        print(name, bp, sp, quantity)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products(name,buying_price,selling_price,stock_quantity)VALUES(%s,%s,%s,%s)", (name, bp, sp, quantity))
        conn.commit()
        return redirect(url_for('products'))

    cur = conn.cursor()
    q = "SELECT * FROM products;"
    cur.execute(q)
    r = cur.fetchall()
    print(r)

    return render_template('products.html', rows=r)


@app.route('/sales')
def sales():
    cur = conn.cursor()
    q = "SELECT s.sid,p.name,p.selling_price,s.quantity,(p.selling_price * s.quantity) AS total,s.created_at FROM products p JOIN sales s ON p.id = s.pid;"
    cur.execute(q)
    b = cur.fetchall()
    print(b)
    return render_template('sales.html', b=b)


@app.route('/dashboard')
def dashboard():
    cur = conn.cursor()
    q = " SELECT sum(products.selling_price * sales.quantity) AS total_sales,products.name FROM products JOIN sales ON products.id = sales.pid GROUP BY products.id;"
    cur.execute(q)
    s = cur.fetchall()
    # print(s)
    labels = []
    data = []
    colours = []
    for i in s:
        labels.append(i[1].split("-")[-1])
        data.append(i[0])
        colours.append("#3cba9f")
    print(labels)
    print(data)

    return render_template('dashboard.html', label=labels, data=data, colours=colours)




if __name__ == "__main__":
    app.run(debug=True)
