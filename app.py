from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# File to store blog posts
POSTS_FILE = 'posts.json'
# File to store user data
USERS_FILE = 'users.json'

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=4)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Initialize with some sample posts if none exist
if not os.path.exists(POSTS_FILE):
    sample_posts = [
        {
            'id': 1,
            'title': 'Welcome to My Blog',
            'content': 'This is my first blog post! Welcome to my blog. I created this using Flask and it has been an amazing journey learning web development.',
            'author': 'Admin',
            'date_posted': 'June 20, 2023'
        },
        {
            'id': 2,
            'title': 'Getting Started with Flask',
            'content': 'Flask is a micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries. It has no database abstraction layer, form validation, or any other components where pre-existing third-party libraries provide common functions.',
            'author': 'Admin',
            'date_posted': 'June 21, 2023'
        }
    ]
    save_posts(sample_posts)

# Initialize with a default admin user if none exist
if not os.path.exists(USERS_FILE):
    default_user = {
        'username': 'admin',
        'password': generate_password_hash('password'),
        'email': 'admin@example.com'
    }
    save_users([default_user])

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/animated')
def animated_blog():
    posts = load_posts()
    return render_template('animated_blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    posts = load_posts()
    post_item = None
    for post in posts:
        if post['id'] == post_id:
            post_item = post
            break
    
    if post_item is None:
        flash('Post not found!', 'error')
        return redirect(url_for('index'))
        
    return render_template('post.html', post=post_item)

@app.route('/create', methods=['GET', 'POST'])
def create():
    # Check if user is logged in
    if 'username' not in session:
        flash('You need to login first!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Create new post
        posts = load_posts()
        new_id = max([post['id'] for post in posts], default=0) + 1
        
        new_post = {
            'id': new_id,
            'title': title,
            'content': content,
            'author': session['username'],
            'date_posted': datetime.now().strftime('%B %d, %Y')
        }
        
        posts.append(new_post)
        save_posts(posts)
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        users = load_users()
        
        # Check if username already exists
        if any(user['username'] == username for user in users):
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = {
            'username': username,
            'password': generate_password_hash(password),
            'email': email
        }
        
        users.append(new_user)
        save_users(users)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        user = next((user for user in users if user['username'] == username), None)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    # Check if user is logged in
    if 'username' not in session:
        flash('You need to login first!', 'error')
        return redirect(url_for('login'))
    
    posts = load_posts()
    post_to_delete = next((post for post in posts if post['id'] == post_id), None)
    
    # Check if post exists and user is the author
    if post_to_delete and post_to_delete['author'] == session['username']:
        posts = [post for post in posts if post['id'] != post_id]
        save_posts(posts)
        flash('Post deleted successfully!', 'success')
    else:
        flash('You can only delete your own posts!', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)