# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import secrets
from geocoding import get_latitude_longitude
from textblob import TextBlob
from flask_login import current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data2.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

chat_history = []

responses = {
    "hi": "Hi!, How can I assist you today?",
    "hello": "Hi there! How can I support you today?",
    "how are you": "I'm an AI, so I don't have feelings, but I'm here to listen to you.",
    "bye": "Take care! Remember, I'm here whenever you need to talk.",
    "feeling anxious": "I'm here to help. When you're anxious, try taking deep breaths and focusing on the present moment.",
    "feeling sad": "I'm here to help. When you're sad, try taking deep breaths and focusing on the present moment.",
    "lonely": "You're not alone. Reach out to friends, family, or a support group when you're feeling lonely.",
    "depressed": "It's okay to feel down. Consider engaging in activities you enjoy or talking to a professional.",
    "suicidal thoughts": "I'm really sorry to hear that, but I can't provide the help you need. Please talk to a mental health professional or a helpline.",
    "coping strategies": "When you're stressed, practicing mindfulness and relaxation techniques can be helpful.",
    "seeking help": "While I'm here to chat, it's important to consult a mental health expert for personalized guidance.",
    "self-care": "Taking care of yourself is important. Make sure you're getting enough rest, eating well, and staying hydrated.",
    "challenging times": "Life can be tough, but you have the strength to overcome challenges.",
    "positive affirmations": "Repeat positive affirmations to boost your mood and self-esteem.",
    "therapy": "Therapy can be a valuable resource. Consider speaking with a therapist who can provide specialized support.",
    "reaching out": "Don't hesitate to reach out to a trusted friend or family member when you need to talk.",
    "progress": "Every step forward, no matter how small, is a step in the right direction.",
    "default": "Sorry, could You please elaborate."
}

def get_bot_response(user_input):
    user_input = user_input.lower()
    for keyword in responses:
        if keyword in user_input:
            return responses[keyword]
    return responses["default"]

def get_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity < 0:
        return 'negative'
    else:
        return 'neutral'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    posts = db.relationship('Post', backref='location', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='posts')
    sentiment = db.Column(db.String(10))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('posts'))
        else:
            flash('User not found. Please try again with a valid username.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('signup'))
        else:
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in with your username.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')



@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    if request.method == 'POST':
        content = request.form.get('content')
        location_name = request.form.get('location')

        location = Location.query.filter_by(name=location_name).first()
        if not location:
            latitude, longitude = get_latitude_longitude(location_name)
            location = Location(name=location_name, latitude=latitude, longitude=longitude)
            db.session.add(location)
            db.session.commit()

        new_post = Post(content=content, location=location, author=current_user)  # Set the author to current_user
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.filter_by(author=current_user)  # Filter posts by current user
    return render_template('posts.html', posts=posts)


@app.route('/feed')
def feed():
    posts = Post.query.all()
    for post in posts:
        post.sentiment = get_sentiment(post.content)
    return render_template('feed.html', posts=posts)

@app.route('/userfeed')
def userfeed():
    posts = Post.query.all() 
    for post in posts:
        post.sentiment = get_sentiment(post.content)
    return render_template('userfeed.html', posts=posts)

    
@app.route('/reco')
def reco():
    # Update sentiment for each post
    posts = Post.query.all()

    # Update sentiment for each post
    for post in posts:
        post.sentiment = get_sentiment(post.content)

    # Create a set to track seen locations
    seen_locations = set()

    # Filter posts with positive sentiment and unique locations
    unique_positive_posts = []
    for post in posts:
        if post.sentiment == 'positive' and post.location not in seen_locations:
            unique_positive_posts.append(post)
            seen_locations.add(post.location)

    return render_template('reco.html', positive_posts=unique_positive_posts)

@app.route('/chat', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_message = request.form.get('user_message')
        if user_message.strip() != "":
            bot_response = get_bot_response(user_message)
            chat_history.append({"user": user_message, "bot": bot_response})

    return render_template('chatbot.html', chat_history=chat_history)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    posts = Post.query.filter(Post.content.ilike(f'%{query}%')).all()
    for post in posts:
        post.sentiment = get_sentiment(post.content)
    return render_template('userfeed.html', posts=posts)

@app.route('/post_experience', methods=['POST'])
@login_required
def post_experience():
    content = request.form['content']
    location = request.form['location']
    return redirect(url_for('userfeed'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
