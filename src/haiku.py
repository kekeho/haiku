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
        # TODO: ログインされていなかったら、/loginにリダイレクト
        return render_template("post.html")
    else:
        # POST
        # TODO: フロントから受け取った俳句を、データベースに保存する
        pass


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # POST
        # TODO: パスワードが合っていたら、cookieをset
        pass


@app.route("/<username>", methods=["GET"])
def index(username: str):
    # TODO: データベースからユーザーが過去に投稿した俳句を抜き出し、レンダリング

    return render_template("index.html", name=username)
