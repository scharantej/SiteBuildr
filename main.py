
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Tutorial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(120), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('tutorial.id'), nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('tutorial.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tutorials')
def tutorials():
    tutorials = Tutorial.query.all()
    return render_template('tutorials.html', tutorials=tutorials)

@app.route('/resources')
def resources():
    resources = Resource.query.all()
    return render_template('resources.html', resources=resources)

@app.route('/forum')
@login_required
def forum():
    return render_template('forum.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/article/<int:id>')
def article(id):
    article = Tutorial.query.get_or_404(id)
    comments = Comment.query.filter_by(tutorial_id=id).all()
    ratings = Rating.query.filter_by(tutorial_id=id).all()
    return render_template('article.html', article=article, comments=comments, ratings=ratings)

@app.route('/resource/<int:id>')
def resource(id):
    resource = Resource.query.get_or_404(id)
    return render_template('resource.html', resource=resource)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Login failed. Check username and password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/comment', methods=['POST'])
@login_required
def comment():
    content = request.form['content']
    author = current_user.username
    tutorial_id = request.form['tutorial_id']
    new_comment = Comment(content=content, author=author, tutorial_id=tutorial_id)
    db.session.add(new_comment)
    db.session.commit()
    flash('Comment added!')
    return redirect(url_for('article', id=tutorial_id))

@app.route('/rating', methods=['POST'])
@login_required
def rating():
    rating = request.form['rating']
    author = current_user.username
    tutorial_id = request.form['tutorial_id']
    new_rating = Rating(rating=rating, author=author, tutorial_id=tutorial_id)
    db.session.add(new_rating)
    db.session.commit()
    flash('Rating added!')
    return redirect(url_for('article', id=tutorial_id))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
