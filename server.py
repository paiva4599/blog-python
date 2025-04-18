from flask import Flask, render_template, request
import os
import datetime
import requests
import smtplib
from dotenv import load_dotenv

load_dotenv()

date = datetime.datetime.now().today().date()
posts_data = requests.get("https://api.npoint.io/674f5423f73deab1e9a7").json()
MY_EMAIL = os.getenv("MY_EMAIL")
PASSWORD = os.getenv("PASSWORD")


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", posts=posts_data, date=date)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]
        header = "Successful sent message!"

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(user=MY_EMAIL, password=PASSWORD)
            smtp.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg=f"Subject: Message from Blog - \n\nUser = {name}\nPhone = {phone}\nEmail = {email}\nMessage = {message}"
            )
    else:
        header = "Contact me"
    return render_template("contact.html", header_info=header)

@app.route("/post/<post_id>")
def post(post_id):
    return render_template("post.html", post_id=post_id, post=posts_data[int(post_id) - 1], date=date)


if __name__ == "__main__":
    app.run(debug=True)