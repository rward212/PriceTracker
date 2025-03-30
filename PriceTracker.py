# TODO: configure lanuchd to run this script every 10 seconds
# TODO: define CSS Selector for each website
# TODO: store CSS Selectors as JSON strings in the database
# TODO: save latest prices to db if price is lower


import pandas as pd
import requests
import sys
import os
import traceback
import smtplib
import schedule
import time
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from price_parser import Price
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from mysqldatabase import get_all_products
from urllib.parse import urlparse
import re

nl = '\n'
load_dotenv()


SAVE_TO_CSV = True
PRICES_CSV = "prices.csv"
FROM_ADDRESS = os.getenv("FROM_ADDRESS")
TO_ADDRESS = os.getenv("TO_ADDRESS")
SUBJECT = "Price Drop Alert"
GMAIL_PASS = os.getenv("GMAIL_PASS")
WEBSITE_SELECTORS = {
    "mountainhardwear.com": ["span[class='value discounted']", "div[class='product__price__rating pt-1']"],
    "carhartt.com": ["span[class='price-range']"],
    "snowpeak.com": ["p.final-price", "span#price"]

}


def fetch_html(url, headers=None):
    """Fetches HTML content from the given URL."""
    try:
        headers = headers or {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_price(soup, selectors):
    """Extracts the price from a given BeautifulSoup object using the given selectors."""
    for selector in selectors:
        price_element = soup.select_one(selector)
        if price_element:
            price_text = price_element.get_text(strip=True)
            price = clean_price(price_text)
            if price:
                return price
    return None


def clean_price(price_text):
    """Extracts a numerical price from a text string."""
    match = re.search(r"[\$€£]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", price_text)
    return float(match.group(1).replace(',', '')) if match else None


def scrape_price(url, selectors):
    """Scrapes the price from a given product URL."""
    domain = urlparse(url).netloc.replace("www.", "")

    # if domain not in WEBSITE_SELECTORS:
    #     raise ValueError("No selectors found for this {domain}")

    html = fetch_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")  # used to have lxml here instead of html.parser
    # selectors = WEBSITE_SELECTORS[domain]

    return extract_price(soup, selectors)


def get_latest_prices():
    """Gets latest prices and returns a dataframe of products that have a price drop."""
    updated_products = []
    for product in get_all_products():
        selectors = product["css_selector"]
        product["price"] = scrape_price(product["url"], selectors)
        product["alert"] = product["price"] < product["alert_price"]
        updated_products.append(product)
    return pd.DataFrame(updated_products)

# builds a pretty hyperlink
def create_hyperlink(text, url):
    return f'<a href="{url}">{text}</a>'


def build_context(df):
    """Generate a list of dicts with product name and price."""
    context = []
    for index in df.index:
        if df['alert'][index]:
            product = {
                'name': create_hyperlink(df['product'][index], df['url'][index]),
                'price': float(df['price'][index])
            }
            context.append(product)
    return context


def load_template(template_path):
    with open(template_path, 'r') as file:
        return file.read()


def build_html_body(context_dict):
    """Build the html body of the email."""
    html_template = load_template('Templates/email_base.html')
    template = Template(html_template)
    html_content = template.render(context=context_dict)
    return html_content


def build_email(html):
    """Build the email message and return a MIME object."""
    email = MIMEMultipart("alternative")
    email["From"] = FROM_ADDRESS
    email["To"] = TO_ADDRESS
    email["Subject"] = SUBJECT
    content = MIMEText(html, "html")
    email.attach(content)
    return email


def send_mail(latest_prices):
    """Sends an email with the latest prices"""
    context = build_context(latest_prices)
    html = build_html_body(context)
    message = build_email(html)
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(FROM_ADDRESS, GMAIL_PASS)
        smtp.sendmail(FROM_ADDRESS, TO_ADDRESS, message.as_string())
    return True

def main():
    schedule.every(10).seconds.do(lambda: send_mail(get_latest_prices()))

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    try:
        rv = main()
    except Exception as err:
        c, i, t = sys.exc_info()
        print(f"\n{os.path.basename(__file__)}: {sys._getframe().f_code.co_name, }()"
              f"EXCEPTION: {err}\n{nl.join(traceback.format_exception(c, i, t))}")
        rv = 1
    sys.exit(rv)
