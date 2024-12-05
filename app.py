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

if __name__ == "__main__":
    app.run(debug=True)
