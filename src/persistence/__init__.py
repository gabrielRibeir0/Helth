"""Camada de persistência (Semana 4)."""

from .week4_persistence import (
    etl_csv_to_postgres,
    index_documents_in_chroma,
    log_event_in_mongo,
    run_three_db_integration_test,
    store_documents_in_mongo,
)

__all__ = [
    "etl_csv_to_postgres",
    "index_documents_in_chroma",
    "log_event_in_mongo",
    "run_three_db_integration_test",
    "store_documents_in_mongo",
]
