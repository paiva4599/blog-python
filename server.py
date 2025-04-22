from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
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
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class AddPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image Url", validators=[DataRequired(), URL()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField("Submit Post")

with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = [post for post in all_posts]
    return render_template("index.html", all_posts=posts)


@app.route('/post/<post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=["POST", "GET"])
def add_post():
    form = AddPostForm()
    exists = request.args.get("exists")
    edit = request.args.get("edit")

    if form.validate_on_submit():
        new_post = BlogPost(
            title= form.title.data,
            subtitle= form.subtitle.data,
            date= date.today().strftime("%B %d, %Y"),
            author= form.author.data,
            body= form.body.data,
            img_url= form.img_url.data
        )

        try:
            db.session.add(new_post)
            db.session.commit()
            flash("Successful created post")
            return redirect(url_for("get_all_posts"))
        except IntegrityError:
            db.session.rollback()
            return redirect(url_for("add_post", exists=True))
    return render_template("make-post.html", form=form, exists=exists, edit=edit)


@app.route('/edit/<post_id>', methods=["POST", "GET"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = AddPostForm(
        title=post.title,
        subtitle=post.subtitle,
        author=post.author,
        body=post.body,
        img_url=post.img_url
    )

    if form.validate_on_submit():
        post.title= form.title.data
        post.subtitle= form.subtitle.data
        post.author= form.author.data
        post.body= form.body.data
        post.img_url= form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=form, edit=True)


@app.route("/remove-post/<post_id>")
def remove_post(post_id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


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



if __name__ == "__main__":
    app.run(debug=True)