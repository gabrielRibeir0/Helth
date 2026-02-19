from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import chromadb
import pandas as pd
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine, text

load_dotenv()


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _build_postgres_url() -> str:
    return (
        f"postgresql+psycopg://{_env('POSTGRES_USER', 'helth_user')}:"
        f"{_env('POSTGRES_PASSWORD', 'change_me_in_production')}@"
        f"{_env('POSTGRES_HOST', 'localhost')}:"
        f"{_env('POSTGRES_PORT', '5432')}/"
        f"{_env('POSTGRES_DB', 'helth_db')}"
    )


def _build_mongo_url() -> str:
    return f"mongodb://{_env('MONGO_HOST', 'localhost')}:{_env('MONGO_PORT', '27017')}/"


def _get_chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=_env("CHROMA_HOST", "localhost"),
        port=int(_env("CHROMA_PORT", "8000")),
    )


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()
    normalized_df.columns = [column.strip() for column in normalized_df.columns]
    for column in normalized_df.select_dtypes(include=["object", "string"]).columns:
        normalized_df[column] = (
            normalized_df[column]
            .astype("string")
            .str.strip()
            .replace(["?", "None", "nan"], pd.NA)
        )
    return normalized_df


def etl_csv_to_postgres(
    csv_path: str,
    table_name: str = "saude_transacional",
    if_exists: str = "replace",
    chunksize: int = 5000,
) -> int:
    df = pd.read_csv(csv_path)
    transformed_df = _normalize_dataframe(df)

    engine = create_engine(_build_postgres_url())
    transformed_df.to_sql(
        table_name,
        engine,
        if_exists=if_exists,
        index=False,
        chunksize=chunksize,
    )
    return len(transformed_df)


def store_documents_in_mongo(
    documents: list[dict],
    collection_name: str = "dataset_documentos",
) -> int:
    if not documents:
        return 0

    client = MongoClient(_build_mongo_url())
    database = client[_env("MONGO_DB", "helth_db")]
    collection = database[collection_name]
    result = collection.insert_many(documents)
    return len(result.inserted_ids)


def log_event_in_mongo(event: dict, collection_name: str = "pipeline_logs") -> str:
    payload = {
        "event": event,
        "created_at": datetime.now(timezone.utc),
    }
    client = MongoClient(_build_mongo_url())
    database = client[_env("MONGO_DB", "helth_db")]
    collection = database[collection_name]
    result = collection.insert_one(payload)
    return str(result.inserted_id)


def _build_embedding_function() -> embedding_functions.DefaultEmbeddingFunction:
    return embedding_functions.DefaultEmbeddingFunction()


def index_documents_in_chroma(
    documents: list[str],
    metadatas: list[dict] | None = None,
    collection_name: str = "helth_embeddings",
) -> int:
    if not documents:
        return 0

    client = _get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=_build_embedding_function(),
    )

    ids = [str(uuid.uuid4()) for _ in documents]
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )
    return len(ids)


def run_three_db_integration_test() -> dict[str, str | int]:
    engine = create_engine(_build_postgres_url())
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    mongo_client = MongoClient(_build_mongo_url())
    mongo_client.admin.command("ping")

    chroma_client = _get_chroma_client()
    chroma_client.heartbeat()

    return {
        "postgres": "ok",
        "mongo": "ok",
        "chroma": "ok",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
