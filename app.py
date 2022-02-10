#from crypt import methods
from flask import Flask, jsonify, make_response, redirect, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = True)
    intro = db.Column(db.String(300), nullable = True)
    text = db.Column(db.Text, nullable = True)
    date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles = articles)

@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article = article)

@app.route('/posts/<int:id>/del')
@auth.login_required
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка"

@app.route('/posts/<int:id>/update', methods=('POST', 'GET'))
def post_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "При обновлении статьи произошла ошибка"
    else:
        return render_template("post-update.html", article = article)

@app.route('/create-article', methods=('POST', 'GET'))
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title = title, intro = intro, text = text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template("create-article.html")


if __name__ == "__main__":
    app.run(debug=True)
