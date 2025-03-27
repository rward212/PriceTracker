# mysqldatabase.py
import mysql.connector
from dotenv import load_dotenv
import os
import json


# Load .env file
load_dotenv()

DATABASE_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}


def get_db_connection():
    return mysql.connector.connect(**DATABASE_CONFIG)


def add_product(name, url, alert_price, css_selector):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, url, alert_price, css_selector)
        VALUES (%s, %s, %s, %s)
    ''', (name, url, alert_price, css_selector))
    conn.commit()
    conn.close()

def update_product(id, name, url, alert_price, css_selector):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products
        SET name = %s, url = %s, alert_price = %s, css_selector = %s
        WHERE id = %s
    ''', (name, url, alert_price, css_selector, id))
    conn.commit()
    conn.close()


def get_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = %s;', (id,))
    product = cursor.fetchone()
    conn.close()
    return product


def get_all_products():
    """Returns a list of dictionaries with all products in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')

    products = [
        {
            'id': database_id,
            'product': product_name,
            'url': url,
            'alert_price': alert_price,
            'css_selector': json.loads(css_selector) # Convert JSON string to Python list
        }
        for database_id, product_name, url, alert_price, css_selector
        in cursor.fetchall()
    ]
    conn.close()
    return products

def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s;', (id,))
    conn.commit()
    conn.close()
    return True

