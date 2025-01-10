# @app.route('/cart')
# def cart():
#     cart_items = session.get('cart', [])
#     total_price = sum(float(item['price']) for item in cart_items)
#     return render_template('cart.html', cart_items=cart_items, total_price=total_price)


# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     product_name = request.form.get('product_name')
#     product_price = request.form.get('product_price')
#     product_image = request.form.get('product_image')
#
#     if 'cart' not in session:
#         session['cart'] = []
#
#     session['cart'].append({
#         'name': product_name,
#         'price': product_price,
#         'image': product_image
#     })
#     session.modified = True
#
#     response = jsonify({
#         'status': 'success',
#         'message': f'{product_name} added to cart!',
#         'cart_count': len(session['cart'])
#     })
#     return response


# @app.route('/remove_from_cart', methods=['POST'])
# def remove_from_cart():
#     item_name = request.form.get('item_name')
#     if 'cart' in session:
#         session['cart'] = [item for item in session['cart'] if item['name'] != item_name]
#         session.modified = True
#     return redirect(url_for('cart'))
#
#
# @app.route('/checkout')
# def checkout():
#     return render_template('checkout.html')


# @app.route("/brand")
# def brand():
#     return render_template("brand.html")


# @app.route("/responsibility")
# def responsibility():
#     return render_template("responsibility.html")


# @app.route("/certifications")
# def certifications():
#     return render_template("certifications.html")
#
#
# @app.route("/faq")
# def faq():
#     return render_template("faq.html")
#
#
# @app.route("/shop/find-your-size")
# def find_your_size():
#     return render_template("find_your_size.html")


# @app.route('/shop')
# def shop():
#     with sqlite3.connect('webshop.db') as conn:
#         c = conn.cursor()
#         # Hent kollektioner og deres tilhørende produkter
#         c.execute('''
#         SELECT collections.id, collections.name, collections.description,
#                products.name, products.description, products.price, products.image
#         FROM collections
#         LEFT JOIN products ON collections.id = products.collection_id
#         ''')
#         rows = c.fetchall()
#
#     # Gruppér data efter kollektion
#     collections = {}
#     for row in rows:
#         collection_id, collection_name, collection_desc, product_name, product_desc, product_price, product_image = row
#         if collection_id not in collections:
#             collections[collection_id] = {
#                 'name': collection_name,
#                 'description': collection_desc,
#                 'products': []
#             }
#         if product_name:  # Hvis der er produkter
#             collections[collection_id]['products'].append({
#                 'name': product_name,
#                 'description': product_desc,
#                 'price': product_price,
#                 'image': product_image
#             })
#
#     return render_template('shop.html', collections=collections)