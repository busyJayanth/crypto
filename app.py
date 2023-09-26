from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
client = MongoClient("mongodb+srv://1by20ec074:crypto@cluster0.xn9q6jv.mongodb.net/?retryWrites=true&w=majority")
db = client["chat_app"]
users = db["users"]
messages = db["messages"]

# Create a key for encrypting and decrypting user data.
key = Fernet.generate_key()
cipher_suite = Fernet(key)


# Routes
@app.route("/")
def home():
    if "username" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.find_one({"username": username})
        if user and cipher_suite.decrypt(user["password"]).decode() == password:
            session["username"] = username
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Encrypt the password before storing it in the database.
        encrypted_password = cipher_suite.encrypt(password.encode())

        user = {"username": username, "password": encrypted_password}
        users.insert_one(user)

        session["username"] = username
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        message = request.form.get("message")
        username = session["username"]

        # Save the message to the database.
        messages.insert_one({"username": username, "message": message})

    chat_messages = messages.find()
    return render_template("chat.html", chat_messages=chat_messages)


if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=5090)
