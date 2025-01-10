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

