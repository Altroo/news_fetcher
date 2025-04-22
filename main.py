import requests
import json

# === Configuration Section ===
# Replace with your actual News API key from your preferred news provider.
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# Replace with your actual OpenRouter API key and endpoint details.
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
# Replace YOUR_ENGINE_ID with the engine/model ID you wish to use.
OPENROUTER_URL = "https://api.openrouter.ai/v1/engines/YOUR_ENGINE_ID/completions"

# Filter themes: adjust these themes as needed.
THEMES = ["technology", "health", "finance"]


# === Functions ===
def fetch_news():
    """
    Fetches news items from the specified news API.
    """
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        return articles
    except Exception as e:
        print("Error fetching news:", e)
        return []


def filter_news_by_theme(articles, themes):
    """
    Filters the list of articles, keeping only those that mention any of the themes.
    """
    filtered = []
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        content = article.get("content", "").lower()
        for theme in themes:
            if theme.lower() in title or theme.lower() in description or theme.lower() in content:
                filtered.append(article)
                break
    return filtered


def summarize_article(article_text):
    """
    Sends the article text to the OpenRouter model to get an abstract (summary).
    """
    # Prepare the prompt for summarization.
    prompt = f"Summarize the following article:\n\n{article_text}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    # Adjust parameters such as max_tokens and temperature per your needs.
    data = {
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.5
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        # Assumes the API returns a structure with choices containing the summary text.
        summary = result.get("choices", [{}])[0].get("text", "").strip()
        return summary
    except Exception as e:
        print("Error summarizing article:", e)
        return "Summary not available."


def save_output(summaries, filename="news_summaries.txt"):
    """
    Saves the list of summaries to a file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for summary in summaries:
                f.write(summary + "\n\n")
        print(f"Summaries successfully saved to {filename}.")
    except Exception as e:
        print("Error saving output:", e)


def main():
    # Step 1: Fetch news articles.
    articles = fetch_news()
    if not articles:
        print("No articles fetched.")
        return

    # Step 2: Filter articles according to the desired themes.
    filtered_articles = filter_news_by_theme(articles, THEMES)
    if not filtered_articles:
        print("No articles match the specified themes.")
        return

    # Step 3: Summarize each filtered article.
    summaries = []
    for article in filtered_articles:
        # Prefer full content if available; otherwise, use the description.
        article_text = article.get("content") or article.get("description") or ""
        if article_text:
            summary = summarize_article(article_text)
        else:
            summary = "No content available."
        formatted = f"Title: {article.get('title', 'No title')}\nSummary: {summary}"
        summaries.append(formatted)

    # Step 4: Save the summaries to a file.
    save_output(summaries)


if __name__ == "__main__":
    main()
