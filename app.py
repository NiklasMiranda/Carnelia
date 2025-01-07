import os
from flask import Flask, render_template, request, redirect, session, make_response, url_for, jsonify
from flask_caching import Cache
import sqlite3
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key_for_development'

login_manager = LoginManager()
login_manager.init_app(app)

admin_user = {
    'username': 'Francesca',
    'password': 'password123',
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username  # Tilføj denne linje

content_file = 'content.json'

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 0
})

conn = sqlite3.connect('webshop.db')
c = conn.cursor()


# Commit and close the connection
conn.commit()
conn.close()


# @app.before_request
# def redirect_to_primary_domain():
#     if not request.host.startswith("www."):
#         return redirect(f"https://www.carnelialingerie.com{request.path}", code=301)

@app.route("/")
@cache.cached(timeout=60)
def home():
    with open('content.json', 'r') as f:
        content = json.load(f)

    username = 'admin'

    # Læs en cookie (hvis den eksisterer)
    username = current_user.username if current_user.is_authenticated else 'Guest'

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

    return render_template("index.html", latest_post=latest_post, username=username, content=content)


@app.route('/setcookie/<username>')
def set_cookie(username):
    resp = make_response(redirect('/'))
    resp.set_cookie('username', username)
    return resp


@app.route('/deletecookie')
def delete_cookie():
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp


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
    cart_items = session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')
    product_image = request.form.get('product_image')

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'name': product_name,
        'price': product_price,
        'image': product_image
    })
    session.modified = True

    response = jsonify({
        'status': 'success',
        'message': f'{product_name} added to cart!',
        'cart_count': len(session['cart'])
    })
    return response


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_name = request.form.get('item_name')
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['name'] != item_name]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route("/brand")
def brand():
    return render_template("brand.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


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


@login_manager.user_loader
def load_user(username):
    return User(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_user['username'] and password == admin_user['password']:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            error = "Forkert brugernavn eller adgangskode"
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logout'))


@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/admin/edit', methods=['GET', 'POST'])
@login_required
def edit_content():
    if request.method == 'POST':
        # Get updated values from the form
        new_title = request.form.get('hero_title')
        new_image = request.form.get('hero_image')
        new_button_text = request.form.get('hero_button_text')

        # Load the current content from JSON
        with open('content.json', 'r') as f:
            content = json.load(f)

        # Update the hero section
        content['hero_section']['title'] = new_title
        content['hero_section']['image'] = new_image
        content['hero_section']['button_text'] = new_button_text

        # Save the updated content back to the JSON file
        with open('content.json', 'w') as f:
            json.dump(content, f, indent=4)

        return redirect(url_for('admin_dashboard'))

    return render_template('edit_content.html')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    with open(content_file, 'r') as f:
        content = json.load(f)

    if request.method == 'POST':
        # Update the Hero Section
        content['hero_section_index']['image'] = request.form['hero_image']
        content['hero_section_index']['title'] = request.form['hero_title']
        content['hero_section_index']['button_text'] = request.form['hero_button_text']
        content['hero_section_index']['button_link'] = request.form['hero_button_link']

        # Update the First Text Block
        content['text_section1_index']['title'] = request.form['text_section1_title']
        content['text_section1_index']['text'] = request.form['text_section1_text']
        content['text_section1_index']['button_text'] = request.form['text_section1_button_text']
        content['text_section1_index']['button_link'] = request.form['text_section1_button_link']

        # Update the Picture Section
        content['picture_section_text_index']['title'] = request.form['picture_section_title']
        content['picture_section_text_index']['text'] = request.form['picture_section_text']
        content['picture_section_text_index']['button_text'] = request.form['picture_section_button_text']
        content['picture_section_text_index']['button_link'] = request.form['picture_section_button_link']

        # Update the Second Text Block
        content['text_section2_index']['title'] = request.form['text_section2_title']
        content['text_section2_index']['text'] = request.form['text_section2_text']

        # Save the updated content back to the JSON file
        with open(content_file, 'w') as f:
            json.dump(content, f, indent=4)

        return redirect(url_for('admin_dashboard'))  # Redirect to show updated data

    return render_template('admin_dashboard.html', content=content)


if __name__ == '__main__':
    app.run(debug=True)
