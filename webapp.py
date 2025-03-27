from mysqldatabase import add_product, get_all_products, delete_product, update_product, get_product
from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)
DATABASE_PATH = "products.sqlite"


@app.route('/')
def index():
    products = get_all_products()
    return render_template('home.html', products=products)


@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        alert_price = request.form['alert_price']
        css_selector = request.form['css_selector']
        add_product(name, url, alert_price, css_selector)
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    delete_product(id)
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    product = get_product(id)

    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        alert_price = request.form['alert_price']
        css_selector = request.form['css_selector']

        update_product(id, name, url, alert_price, css_selector)
        return redirect(url_for('index'))

    return render_template('edit.html', product=product)


if __name__ == '__main__':
    app.run(debug=True)
