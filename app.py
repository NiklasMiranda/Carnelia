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
        # Hent kollektioner og deres tilhørende produkter
        c.execute('''
        SELECT collections.id, collections.name, collections.description, 
               products.name, products.description, products.price, products.image
        FROM collections
        LEFT JOIN products ON collections.id = products.collection_id
        ''')
        rows = c.fetchall()

    # Gruppér data efter kollektion
    collections = {}
    for row in rows:
        collection_id, collection_name, collection_desc, product_name, product_desc, product_price, product_image = row
        if collection_id not in collections:
            collections[collection_id] = {
                'name': collection_name,
                'description': collection_desc,
                'products': []
            }
        if product_name:  # Hvis der er produkter
            collections[collection_id]['products'].append({
                'name': product_name,
                'description': product_desc,
                'price': product_price,
                'image': product_image
            })

    return render_template('shop.html', collections=collections)


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

@app.route("/policies")
def policies():
    return render_template("policies.html")

@app.route("/certifications")
def certifications():
    return render_template("certifications.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/shop/find-your-size")
def find_your_size():
    return render_template("find_your_size.html")

if __name__ == '__main__':
    app.run(debug=True)