import os
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

PG_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
MONGO_URL = "mongodb://localhost:27017/"

def ingest_structured_data(file_path):
    """Insere dados estruturados no PostgreSQL"""
    engine = create_engine(PG_URL)
    df = pd.read_csv(file_path)
    
    df.to_sql('saude_transacional', engine, if_exists='append', index=False, chunksize=10000)
    print(f"Inseridos {len(df)} registos no PostgreSQL.")

def ingest_unstructured_data(json_data):
    """Insere documentos ou logs no MongoDB"""
    client = MongoClient(MONGO_URL)
    db = client['helth_db']
    collection = db['logs_saude']
    
    collection.insert_many(json_data)
    print(f"Inseridos {len(json_data)} documentos no MongoDB.")

if __name__ == "__main__":
    #usar funções para os dados
    pass