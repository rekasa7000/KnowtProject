import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("knowt.json")
app_name = "firebase-admin"  # Use the same app name as in app.py

try:
    firebase_admin.get_app(app_name)
except ValueError:
    firebase_admin.initialize_app(cred, name=app_name)

db = firestore.client(app=firebase_admin.get_app(app_name))

def get_summarized_articles(user_id):
    articles_ref = db.collection('articles').where('user_id', '==', user_id).get()
    summarized_articles = []
    for article in articles_ref:
        article_data = article.to_dict()
        summarized_articles.append({
            'article_id': article.id,  # Include article_id in the dictionary
            'title': article_data['title'],
            'authors': article_data['authors'],
            'publish_date': article_data['publish_date'],
            'summary': article_data['summary'],
            'sentiment': article_data['sentiment'],
            'user_id': article_data['user_id']
        })
    return summarized_articles
