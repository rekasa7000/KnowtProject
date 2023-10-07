import nltk
from textblob import TextBlob
from newspaper import Article
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid

cred = credentials.Certificate("knowt.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def format_publish_date(publish_date):
    if publish_date is not None:
        formatted_date = publish_date.strftime("%B %d, %Y, at %I:%M %p")
        return formatted_date
    else:
        return "Unknown"

def get_article_info(url, user_id):
    article = Article(url)
    article.download()
    article.parse()

    article.nlp()

    title = article.title
    authors = article.authors
    publish_date = article.publish_date
    summary = article.summary

    analysis = TextBlob(article.text)
    polarity = analysis.polarity
    subjectivity = analysis.subjectivity

    if polarity > 0.7:
        sentiment = "This article conveys an extremely positive sentiment!"
    elif polarity > 0.3:
        sentiment = "This article conveys a predominantly positive sentiment."
    elif polarity > 0:
        sentiment = "This article conveys a positive sentiment."
    elif polarity == 0:
        sentiment = "This article is neutral in sentiment."
    elif polarity < -0.7:
        sentiment = "This article conveys an extremely negative sentiment!"
    elif polarity < -0.3:
        sentiment = "This article conveys a predominantly negative sentiment."
    elif polarity < 0:
        sentiment = "This article conveys a negative sentiment."

    formatted_publish_date = format_publish_date(publish_date)

    article_id = str(uuid.uuid4())  # Generate a unique ID for the article

    article_info = {
        'article_id': article_id,  # Add the article_id to the article_info dictionary
        'title': title,
        'authors': authors,
        'publish_date': formatted_publish_date,
        'summary': summary,
        'sentiment': sentiment,
        'user_id': user_id
    }

    # Store the article information in Firestore
    articles_ref = db.collection('articles')
    articles_ref.document(article_id).set(article_info)  # Store the article using the article_id as the document ID

    return article_info
