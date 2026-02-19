#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.persistence.week4_persistence import (
    etl_csv_to_postgres,
    index_documents_in_chroma,
    log_event_in_mongo,
    run_three_db_integration_test,
    store_documents_in_mongo,
)


def _build_documents_from_dataframe(df: pd.DataFrame, limit: int = 50) -> tuple[list[dict], list[str], list[dict]]:
    sample_df = df.head(limit).copy()

    mongo_docs: list[dict] = sample_df.fillna("NA").to_dict(orient="records")

    chroma_docs: list[str] = []
    chroma_metadatas: list[dict] = []
    for index, row in sample_df.iterrows():
        row_map = row.fillna("NA").to_dict()
        text_parts = [f"{key}: {value}" for key, value in row_map.items()]
        chroma_docs.append(" | ".join(text_parts))
        chroma_metadatas.append({"row_index": int(index), "source": "diabetic_data_processed"})

    return mongo_docs, chroma_docs, chroma_metadatas


def main() -> None:
    csv_path = PROJECT_ROOT / "diabetic_data_processed.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            "Ficheiro diabetic_data_processed.csv não encontrado. "
            "Execute primeiro o pipeline em src/ML/diabetic_data.py."
        )

    status = run_three_db_integration_test()
    print(f"Conectividade: {status}")

    inserted_rows = etl_csv_to_postgres(
        csv_path=str(csv_path),
        table_name="saude_transacional",
        if_exists="replace",
    )

    df = pd.read_csv(csv_path)
    mongo_docs, chroma_docs, chroma_metadatas = _build_documents_from_dataframe(df)

    mongo_count = store_documents_in_mongo(mongo_docs, collection_name="dataset_documentos")
    log_id = log_event_in_mongo(
        {
            "stage": "integration_test",
            "message": "Persistência em SQL + NoSQL + Vetorial concluída",
            "rows_sql": inserted_rows,
            "rows_mongo": mongo_count,
            "rows_chroma": len(chroma_docs),
        }
    )
    chroma_count = index_documents_in_chroma(
        documents=chroma_docs,
        metadatas=chroma_metadatas,
        collection_name="helth_embeddings",
    )

    print("--- Resultado integração Semana 4 ---")
    print(f"PostgreSQL (ETL): {inserted_rows} linhas")
    print(f"MongoDB (documentos): {mongo_count} docs")
    print(f"MongoDB (logs): log_id={log_id}")
    print(f"ChromaDB (vetorial): {chroma_count} embeddings")


if __name__ == "__main__":
    main()
