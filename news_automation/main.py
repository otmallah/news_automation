import requests
import logging
import os
import openai

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv
from db_adapter import DBAdapter

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Article:
    title: str
    url: str
    published_date: str
    content: str
    source: str
    is_relevant: bool = False

class NewsScraper:
    def __init__(self, base_url: str, theme: str = "Artificial Intelligence"):
        self.base_url = base_url
        self.theme = theme
        self.articles: List[Article] = []
        self.db_adapter = DBAdapter({
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "database": os.getenv("DB_DATABASE"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        })
        self.setup_openai()

    def setup_openai(self):
        """Initialize OpenAI API with environment variable"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = api_key

    def fetch_articles(self) -> None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36'
        }
        response = requests.get(self.base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get today's and yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_date = yesterday.date()

        # Find all article links
        articles = soup.find_all('a', href=True)
        
        for article in articles:
            href = article['href']
            if href.startswith('/news'):
                article_url = 'https://www.bbc.com' + href
                article_response = requests.get(article_url, headers=headers)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                time_tag = article_soup.find('time')

                if time_tag and time_tag.has_attr('datetime'):
                    published_datetime = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
                    published_date = published_datetime.date()

                    if published_date == yesterday_date:
                        content = ''
                        article_body = article_soup.find('article')
                        if article_body:
                            paragraphs = article_body.find_all('p')
                            content = '\n'.join(p.get_text().strip() for p in paragraphs)

                        title_tag = article_soup.find('h1')
                        title = title_tag.text.strip() if title_tag else 'No title found'
                        self.articles.append(Article(title, article_url, published_date, content, self.base_url, True))

    def filter_articles_by_theme(self) -> None:
        """Filter articles using OpenAI API to check relevance to theme"""
        for article in self.articles:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are a content analyzer. Determine if the following article is related to {self.theme}. Respond with 'yes' or 'no' only."},
                        {"role": "user", "content": f"Title: {article.title}\nContent: {article.content[:1000]}"}
                    ],
                    max_tokens=10
                )
                
                article.is_relevant = response.choices[0].message.content.lower().strip() == 'yes'
                logger.info(f"Article '{article.title}' relevance: {article.is_relevant}")
            except Exception as e:
                logger.error(f"Error filtering article: {str(e)}")
                article.is_relevant = False

    def save_articles(self) -> None:
        """Save relevant articles to a JSON file"""
        relevant_articles = [
            {
                "title": article.title,
                "url": article.url,
                "published_date": article.published_date,
                "source": article.source,
                "content": article.content
            }
            for article in self.articles if article.is_relevant
        ]
        
        self.db_adapter.save_articles(relevant_articles, "articles")


def main():
    try:
        scraper = NewsScraper(
            base_url="https://www.bbc.com/news",
            theme="Artificial Intelligence"
        )
        
        logger.info("Fetching articles...")
        scraper.fetch_articles()
        
        logger.info(f"Found {len(scraper.articles)} articles from yesterday")
        
        if len(scraper.articles) > 0:
            logger.info("Filtering articles by theme...")
            scraper.filter_articles_by_theme()
            
            logger.info("Saving relevant articles...")
            scraper.save_articles()
        else:
            logger.warning("No articles found to process")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
