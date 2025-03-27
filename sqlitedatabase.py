# database.py
import sqlite3

DATABASE_PATH = "products.sqlite"


def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            url TEXT,
            alert_price REAL
        )
    ''')
    conn.commit()
    conn.close()


def insert_product(name, url, alert_price, css_selector):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, url, alert_price, css_selector)
        VALUES (?, ?, ?, ?)
    ''', (name, url, alert_price, css_selector))
    conn.commit()
    conn.close()


def get_watchlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')

    products = [
        {'id': id, 'product': product_name, 'url': url, 'alert_price': alert_price, 'css_selector': css_selector}
        for id, product_name, url, alert_price, css_selector
        in cursor.fetchall()
    ]
    conn.close()
    return products


create_database()
