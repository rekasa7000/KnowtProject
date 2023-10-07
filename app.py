from flask import Flask, render_template, request, redirect, session
import firebase_admin
from google.cloud import firestore
from firebase_admin import credentials
from firebase_admin import firestore
from article import get_article_info
from display import get_summarized_articles
import pyrebase
from flask import flash

config = {
    "apiKey": "AIzaSyBQxEkEWn5gXvcQQYpJZ0Zt6PWyi2i7UJ8",
    "authDomain": "article-summarizer-9580f.firebaseapp.com",
    "databaseURL": "https://article-summarizer-9580f-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "article-summarizer-9580f",
    "storageBucket": "article-summarizer-9580f.appspot.com",
    "messagingSenderId": "880278798479",
    "appId": "1:880278798479:web:239c623a766acf7e6e30fa",
    "measurementId":  "G-57SZR5L0QQ"
}

app = Flask(__name__)
app.secret_key = 'mysecretkey12345regee'  # Set a secret key for session management

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

cred = credentials.Certificate("knowt.json")

db = firestore.client(app=firebase_admin.get_app(name='firebase-admin'))


# Protect routes that require authentication
def login_required(route_function):
    def decorator(*args, **kwargs):
        if 'user' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect('/login')

    decorator.__name__ = 'protected_route_' + route_function.__name__  # Set a unique name for the wrapper function
    return decorator

def get_user_id():
    if 'user' in session:
        user_token = session['user']
        user_info = auth.get_account_info(user_token)
        user_id = user_info['users'][0]['localId']
        return user_id
    return None

@app.route('/article', methods=['GET', 'POST'])
@login_required
def article():
    if request.method == 'POST':
        url = request.form['url']
        user_id = get_user_id()
        if user_id:
            article_info = get_article_info(url, user_id)
            return render_template('article.html', article_info=article_info)
        else:
            return redirect('/login')
    return render_template('article.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        url = request.form['url']
        user_id = get_user_id()
        if user_id:
            article_info = get_article_info(url, user_id)
            return render_template('article.html', article_info=article_info)
        else:
            return redirect('/login')
    user_id = get_user_id()
    if user_id:
        summarized_articles = get_summarized_articles(user_id)
        return render_template('index.html', summarized_articles=summarized_articles)
    else:
        return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Login successful, redirect to dashboard or homepage
            session['user'] = user['idToken']  # Store user ID token in the session
            return redirect('/home')
        except Exception as e:
            error_message = str(e)
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).stream()
        if len(list(query)) > 0:
            error_message = 'Email is already registered.'
            return render_template('register.html', error_message=error_message)

        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_info = {
                'email': email,
                'password': password,
                'user_id': user['localId']
            }
            users_ref.document(user['localId']).set(user_info)
            return redirect('/')
        except Exception as e:
            error_message = str(e)
            return render_template('register.html', error_message=error_message)
    return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)  # Remove user from the session
    return redirect('/')

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    article_id = request.form['article_id']
    delete_article(article_id)
    flash('Article successfully deleted', 'success')  # Add this line
    return redirect('/home')

def delete_article(article_id):
    article_ref = db.collection('articles').document(article_id)
    article_ref.delete()

@app.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    user_id = get_user_id()
    summarized_articles = get_summarized_articles(user_id)
    return render_template('view.html', summarized_articles=summarized_articles)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
