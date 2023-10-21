from flask import Flask, render_template, request
import db

app = Flask(__name__)

db.Base.metadata.create_all(bind=db.engine)


@app.route("/", methods=["GET"])
def root():
    return render_template("root.html")


@app.route("/post", methods=["GET", "POST"])
def post():
    if request.method == "GET":
        return render_template("post.html")
    else:
        # POST
        pass


@app.route("/<username>", methods=["GET"])
def index(username: str):
    return render_template("index.html", name=username)
