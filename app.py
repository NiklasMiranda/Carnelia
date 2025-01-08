import os
from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for, jsonify
from flask_caching import Cache
import sqlite3
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from werkzeug.utils import secure_filename
from flask_sitemap import Sitemap

load_dotenv()

app = Flask(__name__)
ext = Sitemap(app=app)

login_manager = LoginManager()
login_manager.init_app(app)

admin_user = {
    'username': os.environ.get('ADMIN_USERNAME'),
    'password': os.environ.get('ADMIN_PASSWORD'),
}

UPLOAD_FOLDER = 'static/assets/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'assets', 'img')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    print("Entering home function")
    with open('content.json', 'r') as f:
        content = json.load(f)

    print("Loaded content and set username")

    # Læs en cookie (hvis den eksisterer)
    username = current_user.username if current_user.is_authenticated else 'Guest'
    print(f"Username: {username}")

    # Substack RSS-feed URL
    rss_url = "https://carnelialingerie.substack.com/feed"

    # Parse RSS-feedet
    feed = feedparser.parse(rss_url)
    print("Parsed RSS feed")

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
    print("Rendering index.html")
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
    # Load content from JSON file
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        content = {
            'hero_section_index': {'image': '', 'title': '', 'button_text': '', 'button_link': ''},
            'text_section1_index': {'title': '', 'text': '', 'button_text': '', 'button_link': ''},
            'picture_section_text_index': {'image': '', 'title': '', 'text': '', 'button_text': '', 'button_link': ''},
            'text_section2_index': {'title': '', 'text': ''},
            'metadata_index': {'og_title': '', 'og_description': ''},
            'page_metadata': {'title': '', 'meta_description': ''}
        }

    if request.method == 'POST':
        try:
            # Handle new image upload
            if 'new_image' in request.files:
                file = request.files['new_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('Image uploaded successfully!', 'success')
                else:
                    flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'error')

            # Handle hero image selection
            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_index']['image'] = hero_image

            # Handle picture section image selection
            picture_image = request.form.get('picture_section_image_select')
            if picture_image:
                content['picture_section_text_index']['image'] = picture_image

            # Handle picture section image upload
            if 'picture_section_image_upload' in request.files:
                file = request.files['picture_section_image_upload']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    content['picture_section_text_index']['image'] = filename

            # Update sections
            sections = [
                ('hero_section_index', ['title', 'button_text', 'button_link']),
                ('text_section1_index', ['title', 'text', 'button_text', 'button_link']),
                ('picture_section_text_index', ['image', 'title', 'text', 'button_text', 'button_link']),
                ('text_section2_index', ['title', 'text']),
            ]

            for section, fields in sections:
                for field in fields:
                    form_field = f"{section.split('_')[0]}_{field}"
                    if form_field in request.form:
                        content[section][field] = request.form.get(form_field)

            # Update og_title and og_description
            if 'og_title' in request.form:
                content['metadata_index']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['metadata_index']['og_description'] = request.form.get('og_description')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['page_metadata']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['page_metadata']['meta_description'] = request.form.get('meta_description')

            # Save updated content back to JSON
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content updated successfully', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('admin_dashboard'))

    # List images in the upload folder
    images = [f"/static/assets/img/{img}" for img in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(img)]

    return render_template('admin_dashboard.html', content=content, images=images)


@app.route('/sitemap.xml')
def sitemap():
    return ext.generate()


if __name__ == '__main__':
    app.run(debug=True)
