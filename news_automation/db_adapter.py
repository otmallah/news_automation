import psycopg2
from typing import List

class DBAdapter:
    def __init__(self, db_params: dict):
        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()

    def save_articles(self, articles: List, table_name: str):
        self.create_table(table_name)
        for article in articles:
            self.cursor.execute(f"INSERT INTO {table_name} (title, url, published_date, content, source) VALUES (%s, %s, %s, %s, %s)", (article.get("title"), article.get("url"), article.get("published_date"), article.get("content"), article.get("source")))
        self.conn.commit()

    def create_table(self, table_name: str):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (title TEXT, url TEXT, published_date DATE, content TEXT, source TEXT)")
        self.conn.commit()
