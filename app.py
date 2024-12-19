import os
from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for, jsonify
from flask_caching import Cache
import sqlite3
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key_for_development'

# OAuth2 Configuration
client_id = os.environ.get('OAUTH_CLIENT_ID')
client_secret = os.environ.get('OAUTH_CLIENT_SECRET')
tenant_id = os.environ.get('OAUTH_TENANT_ID')
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
scope = ['https://graph.microsoft.com/Mail.Send']

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 0
})

conn = sqlite3.connect('webshop.db')
c = conn.cursor()


# Commit and close the connection
conn.commit()
conn.close()

def get_oauth2_token():
    try:
        # Create an OAuth2 session
        oauth = OAuth2Session(client_id, redirect_uri='https://carnelia.pythonanywhere.com/callback', scope=scope)

        # Redirect the user to the provider's authorization URL
        authorization_url, state = oauth.authorization_url('https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize')
        print('Please go to %s and authorize access.' % authorization_url)

        # Get the authorization response URL from the user
        redirect_response = input('Paste the full redirect URL here: ')

        # Fetch the access token
        token = oauth.fetch_token(token_url, authorization_response=redirect_response, client_secret=client_secret)
        print("OAuth2 token retrieved:", token)
        return token
    except Exception as e:
        print(f"An error occurred while retrieving the OAuth2 token: {e}")
        return None

def send_email_with_graph_api(subject, body, recipients):
    token = get_oauth2_token()
    if not token:
        print("Failed to retrieve OAuth2 token.")
        return

    access_token = token.get('access_token')
    if not access_token:
        print("Access token is missing in the OAuth2 token.")
        return

    # Create the email message
    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": recipient}} for recipient in recipients
            ]
        }
    }

    try:
        # Send the email using Microsoft Graph API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(
            'https://graph.microsoft.com/v1.0/me/sendMail',
            headers=headers,
            json=email_msg
        )

        if response.status_code == 202:
            print("Email sent successfully.")
        else:
            print(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

@app.route('/callback')
def callback():
    try:
        # Create an OAuth2 session
        oauth = OAuth2Session(client_id, redirect_uri='https://carnelia.pythonanywhere.com/callback', scope=scope)

        # Fetch the access token using the authorization response
        token = oauth.fetch_token(token_url, authorization_response=request.url, client_secret=client_secret)
        print("OAuth2 token retrieved:", token)
        return "Token retrieved successfully!"
    except Exception as e:
        print(f"An error occurred while retrieving the OAuth2 token: {e}")
        return "An error occurred during token retrieval."


@app.route("/")
@cache.cached(timeout=60)
def home():
    # Læs en cookie (hvis den eksisterer)
    username = request.cookies.get('username')

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

    return render_template("index.html", latest_post=latest_post, username=username)


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


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Create the email content
        subject = "New message from contact form"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        recipients = ["info@carnelia.net"]

        # Send the email using Microsoft Graph API
        try:
            send_email_with_graph_api(subject, body, recipients)
            flash("Thank you for contacting us! We'll get back to you soon.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")

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


if __name__ == '__main__':
    app.run(debug=True)
