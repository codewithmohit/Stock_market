import requests
from transformers import pipeline
from datetime import datetime
import time

# --- Configuration ---
NEWS_API_KEY = "835381e530674b2e868673f777b50e70"
TELEGRAM_BOT_TOKEN = "7430660884:AAGuihBn67fVJzsw-VHafctmFAIbbqEXM_o"
TELEGRAM_CHAT_ID = "972584544"
MODEL = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# --- Functions ---
def fetch_news():
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"q=india+stock+market&apiKey={NEWS_API_KEY}&language=en"
    )
    response = requests.get(url)
    articles = response.json().get("articles", [])
    return articles

def analyze_sentiment(text):
    result = MODEL(text[:512])[0]  # limit to 512 chars
    label = result['label']
    return label

def send_telegram_message(message):
    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        f"?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    )
    requests.get(url)

def format_alert(sentiment, title, source):
    trend = {
        "POSITIVE": "📈 Market may go UP",
        "NEGATIVE": "📉 Market may go DOWN",
        "NEUTRAL": "🤷 Neutral impact"
    }.get(sentiment, "❓Unknown")
    return f"{trend}\n📰 *{title}*\nSource: {source}"

def run():
    print(f"[{datetime.now()}] Fetching news...")
    articles = fetch_news()

    for article in articles[:5]:  # Only process top 5
        title = article['title']
        content = article.get('description', '') or ''
        source = article['source']['name']
        text = f"{title}. {content}"

        sentiment = analyze_sentiment(text)
        alert = format_alert(sentiment, title, source)
        print(alert)
        send_telegram_message(alert)
        time.sleep(2)  # To avoid hitting Telegram rate limits

if __name__ == "__main__":
    run()
