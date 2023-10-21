from flask import Flask, render_template
import db

app = Flask(__name__)

db.Base.metadata.create_all(bind=db.engine)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/post")
def post():
    return render_template("post.html")
