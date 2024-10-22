from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_session import Session
from pymongo import MongoClient
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.flask_app
users_collection = db.users
tasks_collection = db.tasks

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        tasks = list(tasks_collection.find({'username': username}))
        return render_template('index.html', tasks=tasks)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = {
            'username': form.username.data,
            'password': hashed_password
        }
        users_collection.insert_one(user)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users_collection.find_one({'username': form.username.data})
        if user and check_password_hash(user['password'], form.password.data):
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' in session:
        username = session['username']
        task_content = request.form['content']
        task = {
            'username': username,
            'content': task_content,
        }
        tasks_collection.insert_one(task)
        flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    if 'username' in session:
        task = tasks_collection.find_one({'_id': ObjectId(task_id)})
        if task and task['username'] == session['username']:
            tasks_collection.delete_one({'_id': ObjectId(task_id)})
            flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/update_task/<task_id>', methods=['POST'])
def update_task(task_id):
    if 'username' in session:
        new_content = request.form['content']
        tasks_collection.update_one({'_id': ObjectId(task_id)}, {'$set': {'content': new_content}})
        flash('Task updated successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
