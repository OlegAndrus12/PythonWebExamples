import requests
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
app = Flask(__file__)


@app.route("/")
def index():
    query = request.args.get("query", "latest")
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    news_data = response.json()
    
    return render_template("index.html", articles = news_data.get("articles", []), query=query)

app.run(host="0.0.0.0", port=3000)
