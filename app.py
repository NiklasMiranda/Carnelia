from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def home():
    return render_template("index.html")

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

@app.route("/responsibility/self-defined-feminity")
def responsibility_self_defined_feminity():
    return render_template("responsibility_self_defined_feminity.html")

@app.route("/responsibility/eco-consciousness")
def responsibility_eco_consciousness():
    return render_template("responsibility_eco_consciousness.html")

@app.route("/shop/find-your-size")
def find_your_size():
    return render_template("find_your_size.html")

if __name__ == '__main__':
    app.run(debug=True)