from flask import Flask, render_template, request, redirect, flash, session
from flask_caching import Cache
import sqlite3
import feedparser
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

conn = sqlite3.connect('webshop.db')
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT,
    stock_quantity INTEGER NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

test_products = [
    ("Laptop", "A high-performance laptop", 999.99, "laptop.jpg", 10),
    ("Smartphone", "A latest-gen smartphone", 699.99, "smartphone.jpg", 25),
    ("Headphones", "Noise-cancelling headphones", 199.99, "headphones.jpg", 50),
    ("Smartwatch", "A sleek smartwatch", 249.99, "smartwatch.jpg", 15)
]

c.executemany('''
INSERT INTO products (name, description, price, image, stock_quantity)
VALUES (?, ?, ?, ?, ?)
''', test_products)

# Commit and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")

@app.route("/")
@cache.cached(timeout=60)
def home():
    # Substack RSS-feed URL
    rss_url = "https://carnelialingerie.substack.com/feed"

    # Parse RSS-feedet
    feed = feedparser.parse(rss_url)

    # Hent den seneste post
    latest_post = None
    if feed.entries:
        entry = feed.entries[0]

        # Find billed-URL (hvis tilgængelig)
        image_url = None
        if 'content' in entry:
            soup = BeautifulSoup(entry.content[0].value, 'html.parser')
            img_tag = soup.find('img')
            if img_tag:
                image_url = img_tag['src']
        elif 'summary' in entry:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img_tag = soup.find('img')
            if img_tag:
                image_url = img_tag['src']

        # Tilføj post-data
        latest_post = {
            "title": entry.title,
            "summary": entry.summary,
            "published": entry.published,
            "link": entry.link,
            "image": image_url
        }

    return render_template("index.html", latest_post=latest_post)


@app.route('/shop')
def shop():
    with sqlite3.connect('webshop.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, description, price, image FROM products')
        products = c.fetchall()
    return render_template('shop.html', products=products)


@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route("/brand")
def brand():
    return render_template("brand.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/submit-form", methods=["POST"])
def submit_form():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Her kan du gemme eller behandle dataen, f.eks. sende en e-mail eller logge den
    print(f"Name: {name}, Email: {email}, Message: {message}")
    flash("Thank you for contacting us! We'll get back to you soon.")
    return redirect("/")

@app.route("/responsibility")
def responsibility():
    return render_template("responsibility.html")

@app.route("/brand/community")
def brand_community():
    return render_template("brand_community.html")

@app.route("/brand/purpose")
def brand_purpose():
    return render_template("brand_purpose.html")

@app.route("/responsibility/comfort")
def responsibility_comfort():
    return render_template("responsibility_comfort.html")

@app.route("/responsibility/self-defined-femininity")
def responsibility_self_defined_femininity():
    return render_template("responsibility_self_defined_femininity.html")

@app.route("/responsibility/eco-consciousness")
def responsibility_eco_consciousness():
    return render_template("responsibility_eco_consciousness.html")

@app.route("/shop/find-your-size")
def find_your_size():
    return render_template("find_your_size.html")

if __name__ == '__main__':
    app.run(debug=True)