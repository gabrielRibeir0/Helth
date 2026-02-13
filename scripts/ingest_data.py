import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine

load_dotenv()

PG_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
MONGO_URL = "mongodb://localhost:27017/"

def ingest_structured_data(file_path):
    engine = create_engine(PG_URL)
    df = pd.read_csv(file_path)
    df.to_sql('saude_transacional', engine, if_exists='append', index=False, chunksize=10000)
    print(f"Inseridos {len(df)} registos no PostgreSQL.")

def ingest_unstructured_data(json_data):
    client = MongoClient(MONGO_URL)
    db = client['helth_db']
    collection = db['logs_saude']
    collection.insert_many(json_data)
    print(f"Inseridos {len(json_data)} documentos no MongoDB.")

def ingest_bbc_health_news(): # vai ser usado como terceira fonte (crawler)

    url = "https://www.bbc.com/news/health"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erro ao fazer pedido http: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2')

        news_data = []
        for h in headlines:
            title = h.get_text().strip()
            link_tag = h.find_parent('a')
            link = f"https://www.bbc.com{link_tag['href']}" if link_tag else "N/A"

            if title:
                news_data.append({
                    "source": "BBC Health",
                    "title": title,
                    "url": link,
                    "crawled_at": datetime.now()
                })

        news_data = news_data[:20] # seleciona 20 noticias

        if not news_data:
            print("nenhuma notícia encontrada")
            return

        # parte de inserção no mongodb
        client = MongoClient(MONGO_URL)
        db = client['helth_db']
        collection = db['noticias_saude']

        # nao apaga os dados antigos
        collection.insert_many(news_data)

        print(f"sucesso: {len(news_data)} notícias guardadas no mongodb.")

    except Exception as e:
        print(f"erro no crawler: {e}")

if __name__ == "__main__":

    # ingest_bbc_health_news()
    pass
