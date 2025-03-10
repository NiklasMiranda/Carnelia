import os
from flask import (Flask, render_template, request, redirect, flash, make_response,
                   url_for)
from flask_caching import Cache
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key_for_development'

login_manager = LoginManager()
login_manager.init_app(app)

content_file = 'content.json'

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


cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 0
})


# @app.before_request
# def redirect_to_primary_domain():
#     if not request.host.startswith("www."):
#         return redirect(f"https://127.0.0.1:5000{request.path}", code=301)


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


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/brand/community")
def brand_community():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("brand_community.html", content=content)


@app.route("/brand/purpose")
def brand_purpose():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("brand_purpose.html", content=content)


@app.route("/responsibility/comfort")
def responsibility_comfort():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("responsibility_comfort.html", content=content)


@app.route("/responsibility/self-defined-femininity")
def responsibility_self_defined_femininity():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("responsibility_self_defined_femininity.html", content=content)


@app.route("/responsibility/eco-consciousness")
def responsibility_eco_consciousness():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("responsibility_eco_consciousness.html", content=content)


@app.route("/policies")
def policies():
    with open('content.json', 'r') as f:
        content = json.load(f)
    return render_template("policies.html", content=content)


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
    return redirect(url_for('logout_page'))


@app.route('/logout_page')
def logout_page():
    return render_template('logout.html')


@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Indlæs JSON-indhold
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default struktur, hvis filen ikke findes eller ikke kan læses
        content = {
            'hero_section_brand_community': {'image': '', 'title': '', 'button_text': '', 'button_link': ''},
            'text_section1_brand_community': {'title': '', 'text': '', 'button_text': '', 'button_link': ''},
            'picture_section_text_brand_community': {'image': '', 'title': '', 'text': '', 'button_text': '',
                                                     'button_link': ''},
            'text_section2_brand_community': {'title': '', 'text': ''},
            'metadata_brand_community': {'title': '', 'meta_description': ''},
            'opengraph_brand_community': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Håndtering af billedupload
            if 'new_image' in request.files:
                file = request.files['new_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('Billedet blev uploadet med succes!', 'success')
                else:
                    flash('Ugyldig filtype. Tilladte typer er png, jpg, jpeg, gif.', 'error')

            # Opdatering af billeder
            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_index']['image'] = hero_image

            picture_image = request.form.get('picture_section_image_select')
            if picture_image:
                content['picture_section_text_index']['image'] = picture_image

            # Opdatering af sektioner

            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_index']['title'] = request.form.get('hero_title')
            if 'hero_section_index_button_text' in request.form:
                content['hero_section_index']['button_text'] = request.form.get('hero_section_index_button_text')
            if 'hero_section_index_button_link' in request.form:
                content['hero_section_index']['button_link'] = request.form.get('hero_section_index_button_link')

            # Text Section 1
            if 'text_section1_title' in request.form:
                content['text_section1_index']['title'] = request.form.get('text_section1_title')
            if 'text_section1_index_text' in request.form:
                content['text_section1_index']['text'] = request.form.get('text_section1_index_text')
            if 'text_section1_index_button_text' in request.form:
                content['text_section1_index']['button_text'] = request.form.get('text_section1_index_button_text')
            if 'text_section1_index_button_link' in request.form:
                content['text_section1_index']['button_link'] = request.form.get('text_section1_index_button_link')

            # Picture Section
            if 'picture_section_text_index_title' in request.form:
                content['picture_section_text_index']['title'] = request.form.get('picture_section_text_index_title')
            if 'picture_section_text_index_text' in request.form:
                content['picture_section_text_index']['text'] = request.form.get('picture_section_text_index_text')
            if 'picture_section_text_index_button_text' in request.form:
                content['picture_section_text_index']['button_text'] = request.form.get(
                    'picture_section_text_index_button_text')
            if 'picture_section_text_index_button_link' in request.form:
                content['picture_section_text_index']['button_link'] = request.form.get(
                    'picture_section_text_index_button_link')

            # Text Section 2
            if 'text_section2_index_title' in request.form:
                content['text_section2_index']['title'] = request.form.get('text_section2_index_title')
            if 'text_section2_index_text' in request.form:
                content['text_section2_index']['text'] = request.form.get('text_section2_index_text')

            # Opdatering af sidetitel og meta description
            if 'page_title' in request.form:
                content['metadata_index']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_index']['meta_description'] = request.form.get('meta_description')

            # Opdatering af metadata
            if 'og_title' in request.form:
                content['opengraph_index']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_index']['og_description'] = request.form.get('og_description')

            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_dashboard'))

    # Hent billeder fra upload-mappen
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_dashboard.html', content=content, images=images)


@app.route('/admin_dashboard_brand_community', methods=['GET', 'POST'])
@login_required
def admin_brand_community():
    # Load JSON content
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure if the file does not exist or cannot be read
        content = {
            'hero_section_brand_community': {'title': '', 'image': ''},
            'text_section_brand_community': {'title': '', 'text': ''},
            'picture_section_text1_brand_community': {'image': '', 'title': '', 'text': ''},
            'picture_section_text2_brand_community': {'image': '', 'title': '', 'text': ''},
            'metadata_brand_community': {'title': '', 'meta_description': ''},
            'opengraph_brand_community': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Update images

            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_brand_community']['image'] = hero_image

            picture_image1 = request.form.get('picture_section1_image_select')
            if picture_image1:
                content['picture_section_text1_brand_community']['image'] = picture_image1

            picture_image2 = request.form.get('picture_section2_image_select')
            if picture_image2:
                content['picture_section_text2_brand_community']['image'] = picture_image2

            # Update sections
            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_brand_community']['title'] = request.form.get('hero_title')

            # Text Section
            if 'text_section_title' in request.form:
                content['text_section_brand_community']['title'] = request.form.get('text_section_title')
            if 'text_section_text' in request.form:
                content['text_section_brand_community']['text'] = request.form.get('text_section_text')

            # Picture Section 1
            if 'picture_section1_title' in request.form:
                content['picture_section_text1_brand_community']['title'] = request.form.get(
                    'picture_section1_title')
            if 'picture_section1_text' in request.form:
                content['picture_section_text1_brand_community']['text'] = request.form.get(
                    'picture_section1_text')

            # Picture Section 2
            if 'picture_section2_title' in request.form:
                content['picture_section_text2_brand_community']['title'] = request.form.get(
                    'picture_section2_title')
            if 'picture_section2_text' in request.form:
                content['picture_section_text2_brand_community']['text'] = request.form.get(
                    'picture_section2_text')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['metadata_brand_community']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_brand_community']['meta_description'] = request.form.get('meta_description')

            # Update metadata
            if 'og_title' in request.form:
                content['opengraph_brand_community']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_brand_community']['og_description'] = request.form.get('og_description')

            # Save updated content back to the JSON file
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_brand_community'))

    # Fetch images from the upload folder
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_brand_community.html', content=content, images=images)


@app.route('/admin_dashboard_brand_purpose', methods=['GET', 'POST'])
@login_required
def admin_brand_purpose():
    # Load JSON content
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure if the file does not exist or cannot be read
        content = {
            'hero_section_brand_purpose': {'title': '', 'image': ''},
            'text_section_brand_purpose': {'title': '', 'text': ''},
            'picture_section_text1_brand_purpose': {'image': '', 'title': '', 'text': ''},
            'picture_section_text2_brand_purpose': {'image': '', 'title': '', 'text': ''},
            'metadata_brand_purpose': {'title': '', 'meta_description': ''},
            'opengraph_brand_purpose': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Update images

            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_brand_purpose']['image'] = hero_image

            picture_image1 = request.form.get('picture_section1_image_select')
            if picture_image1:
                content['picture_section_text1_brand_purpose']['image'] = picture_image1

            picture_image2 = request.form.get('picture_section2_image_select')
            if picture_image2:
                content['picture_section_text2_brand_purpose']['image'] = picture_image2

            # Update sections
            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_brand_purpose']['title'] = request.form.get('hero_title')

            # Text Section
            if 'text_section_title' in request.form:
                content['text_section_brand_purpose']['title'] = request.form.get('text_section_title')
            if 'text_section_text' in request.form:
                content['text_section_brand_purpose']['text'] = request.form.get('text_section_text')

            # Picture Section 1
            if 'picture_section1_title' in request.form:
                content['picture_section_text1_brand_purpose']['title'] = request.form.get(
                    'picture_section1_title')
            if 'picture_section1_text' in request.form:
                content['picture_section_text1_brand_purpose']['text'] = request.form.get(
                    'picture_section1_text')

            # Picture Section 2
            if 'picture_section2_title' in request.form:
                content['picture_section_text2_brand_purpose']['title'] = request.form.get(
                    'picture_section2_title')
            if 'picture_section2_text' in request.form:
                content['picture_section_text2_brand_purpose']['text'] = request.form.get(
                    'picture_section2_text')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['metadata_brand_purpose']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_brand_purpose']['meta_description'] = request.form.get('meta_description')

            # Update metadata
            if 'og_title' in request.form:
                content['opengraph_brand_purpose']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_brand_purpose']['og_description'] = request.form.get('og_description')

            # Save updated content back to the JSON file
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_brand_purpose'))

    # Fetch images from the upload folder
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_brand_purpose.html', content=content, images=images)


@app.route('/admin_dashboard_responsibility_comfort', methods=['GET', 'POST'])
@login_required
def admin_responsibility_comfort():
    # Load JSON content
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure if the file does not exist or cannot be read
        content = {
            'hero_section_responsibility_comfort': {'title': '', 'image': ''},
            'text_section_responsibility_comfort': {'title': '', 'text': ''},
            'picture_section_text1_responsibility_comfort': {'image': '', 'title': '', 'text': ''},
            'picture_section_text2_responsibility_comfort': {'image': '', 'title': '', 'text': ''},
            'picture_section_text3_responsibility_comfort': {'image': '', 'title': '', 'text': ''},
            'metadata_responsibility_comfort': {'title': '', 'meta_description': ''},
            'opengraph_responsibility_comfort': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Update images

            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_responsibility_comfort']['image'] = hero_image

            picture_image1 = request.form.get('picture_section1_image_select')
            if picture_image1:
                content['picture_section_text1_responsibility_comfort']['image'] = picture_image1

            picture_image2 = request.form.get('picture_section2_image_select')
            if picture_image2:
                content['picture_section_text2_responsibility_comfort']['image'] = picture_image2

            picture_image3 = request.form.get('picture_section3_image_select')
            if picture_image3:
                content['picture_section_text3_responsibility_comfort']['image'] = picture_image3

            # Update sections
            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_responsibility_comfort']['title'] = request.form.get('hero_title')

            # Text Section
            if 'text_section_title' in request.form:
                content['text_section_responsibility_comfort']['title'] = request.form.get('text_section_title')
            if 'text_section_text' in request.form:
                content['text_section_responsibility_comfort']['text'] = request.form.get('text_section_text')

            # Picture Section 1
            if 'picture_section1_title' in request.form:
                content['picture_section_text1_responsibility_comfort']['title'] = request.form.get(
                    'picture_section1_title')
            if 'picture_section1_text' in request.form:
                content['picture_section_text1_responsibility_comfort']['text'] = request.form.get(
                    'picture_section1_text')

            # Picture Section 2
            if 'picture_section2_title' in request.form:
                content['picture_section_text2_responsibility_comfort']['title'] = request.form.get(
                    'picture_section2_title')
            if 'picture_section2_text' in request.form:
                content['picture_section_text2_responsibility_comfort']['text'] = request.form.get(
                    'picture_section2_text')

            # Picture Section 3
            if 'picture_section3_title' in request.form:
                content['picture_section_text3_responsibility_comfort']['title'] = request.form.get(
                    'picture_section3_title')
            if 'picture_section3_text' in request.form:
                content['picture_section_text3_responsibility_comfort']['text'] = request.form.get(
                    'picture_section3_text')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['metadata_responsibility_comfort']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_responsibility_comfort']['meta_description'] = request.form.get('meta_description')

            # Update metadata
            if 'og_title' in request.form:
                content['opengraph_responsibility_comfort']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_responsibility_comfort']['og_description'] = request.form.get('og_description')

            # Save updated content back to the JSON file
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_responsibility_comfort'))

    # Fetch images from the upload folder
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_responsibility_comfort.html', content=content, images=images)


@app.route('/admin_dashboard_responsibility_eco_consciousness', methods=['GET', 'POST'])
@login_required
def admin_responsibility_eco_consciousness():
    # Load JSON content
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure if the file does not exist or cannot be read
        content = {
            'hero_section_responsibility_eco_consciousness': {'title': '', 'image': ''},
            'text_section_responsibility_eco_consciousness': {'title': '', 'text': ''},
            'picture_section_text1_responsibility_eco_consciousness': {'image': '', 'title': '', 'text': ''},
            'picture_section_text2_responsibility_eco_consciousness': {'image': '', 'title': '', 'text': ''},
            'metadata_responsibility_eco_consciousness': {'title': '', 'meta_description': ''},
            'opengraph_responsibility_eco_consciousness': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Update images

            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_responsibility_eco_consciousness']['image'] = hero_image

            picture_image1 = request.form.get('picture_section1_image_select')
            if picture_image1:
                content['picture_section_text1_responsibility_eco_consciousness']['image'] = picture_image1

            picture_image2 = request.form.get('picture_section2_image_select')
            if picture_image2:
                content['picture_section_text2_responsibility_eco_consciousness']['image'] = picture_image2

            # Update sections
            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_responsibility_eco_consciousness']['title'] = request.form.get('hero_title')

            # Text Section
            if 'text_section_title' in request.form:
                content['text_section_responsibility_eco_consciousness']['title'] = request.form.get('text_section_title')
            if 'text_section_text' in request.form:
                content['text_section_responsibility_eco_consciousness']['text'] = request.form.get('text_section_text')

            # Picture Section 1
            if 'picture_section1_title' in request.form:
                content['picture_section_text1_responsibility_eco_consciousness']['title'] = request.form.get(
                    'picture_section1_title')
            if 'picture_section1_text' in request.form:
                content['picture_section_text1_responsibility_eco_consciousness']['text'] = request.form.get(
                    'picture_section1_text')

            # Picture Section 2
            if 'picture_section2_title' in request.form:
                content['picture_section_text2_responsibility_eco_consciousness']['title'] = request.form.get(
                    'picture_section2_title')
            if 'picture_section2_text' in request.form:
                content['picture_section_text2_responsibility_eco_consciousness']['text'] = request.form.get(
                    'picture_section2_text')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['metadata_responsibility_eco_consciousness']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_responsibility_eco_consciousness']['meta_description'] = request.form.get('meta_description')

            # Update metadata
            if 'og_title' in request.form:
                content['opengraph_responsibility_eco_consciousness']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_responsibility_eco_consciousness']['og_description'] = request.form.get('og_description')

            # Save updated content back to the JSON file
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_responsibility_eco_consciousness'))

    # Fetch images from the upload folder
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_responsibility_eco_consciousness.html', content=content, images=images)


@app.route('/admin_dashboard_responsibility_self_defined_femininity', methods=['GET', 'POST'])
@login_required
def admin_responsibility_self_defined_femininity():
    # Load JSON content
    try:
        with open(content_file, 'r') as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure if the file does not exist or cannot be read
        content = {
            'hero_section_responsibility_self_defined_femininity': {'title': '', 'image': ''},
            'text_section_responsibility_self_defined_femininity': {'title': '', 'text': ''},
            'picture_section_text1_responsibility_self_defined_femininity': {'image': '', 'title': '', 'text': ''},
            'picture_section_text2_responsibility_self_defined_femininity': {'image': '', 'title': '', 'text': ''},
            'metadata_responsibility_self_defined_femininity': {'title': '', 'meta_description': ''},
            'opengraph_responsibility_self_defined_femininity': {'og_title': '', 'og_description': ''}
        }

    if request.method == 'POST':
        try:

            # Update images

            hero_image = request.form.get('hero_image_select')
            if hero_image:
                content['hero_section_responsibility_self_defined_femininity']['image'] = hero_image

            picture_image1 = request.form.get('picture_section1_image_select')
            if picture_image1:
                content['picture_section_text1_responsibility_self_defined_femininity']['image'] = picture_image1

            picture_image2 = request.form.get('picture_section2_image_select')
            if picture_image2:
                content['picture_section_text2_responsibility_self_defined_femininity']['image'] = picture_image2

            # Update sections
            # Hero Section
            if 'hero_title' in request.form:
                content['hero_section_responsibility_self_defined_femininity']['title'] = request.form.get('hero_title')

            # Text Section
            if 'text_section_title' in request.form:
                content['text_section_responsibility_self_defined_femininity']['title'] = request.form.get('text_section_title')
            if 'text_section_text' in request.form:
                content['text_section_responsibility_self_defined_femininity']['text'] = request.form.get('text_section_text')

            # Picture Section 1
            if 'picture_section1_title' in request.form:
                content['picture_section_text1_responsibility_self_defined_femininity']['title'] = request.form.get(
                    'picture_section1_title')
            if 'picture_section1_text' in request.form:
                content['picture_section_text1_responsibility_self_defined_femininity']['text'] = request.form.get(
                    'picture_section1_text')

            # Picture Section 2
            if 'picture_section2_title' in request.form:
                content['picture_section_text2_responsibility_self_defined_femininity']['title'] = request.form.get(
                    'picture_section2_title')
            if 'picture_section2_text' in request.form:
                content['picture_section_text2_responsibility_self_defined_femininity']['text'] = request.form.get(
                    'picture_section2_text')

            # Update page title and meta description
            if 'page_title' in request.form:
                content['metadata_responsibility_self_defined_femininity']['title'] = request.form.get('page_title')
            if 'meta_description' in request.form:
                content['metadata_responsibility_self_defined_femininity']['meta_description'] = request.form.get('meta_description')

            # Update metadata
            if 'og_title' in request.form:
                content['opengraph_responsibility_self_defined_femininity']['og_title'] = request.form.get('og_title')
            if 'og_description' in request.form:
                content['opengraph_responsibility_self_defined_femininity']['og_description'] = request.form.get('og_description')

            # Save updated content back to the JSON file
            with open(content_file, 'w') as f:
                json.dump(content, f, indent=4)

            flash('Content successfully updated', 'success')
        except Exception as e:
            flash(f'Error in updating the content: {str(e)}', 'error')

        return redirect(url_for('admin_responsibility_self_defined_femininity'))

    # Fetch images from the upload folder
    images = [
        f"/static/assets/img/{img}"
        for img in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(img)
    ]

    return render_template('admin_responsibility_self_defined_femininity.html', content=content, images=images)


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


if __name__ == '__main__':
    app.run(debug=True)
