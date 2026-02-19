from datetime import datetime
from pathlib import Path
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.persistence.week4_persistence import (  # noqa: E402
    index_documents_in_chroma,
    log_event_in_mongo,
    store_documents_in_mongo,
)

NHS_DIABETES_URL = "https://www.nhs.uk/conditions/diabetes/"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 20
MONGO_COLLECTION_NHS = "nhs_diabetes_content"
CHROMA_COLLECTION_NHS = "nhs_diabetes_embeddings"
NHS_NAVIGATING_LINKS = {
 'Type 1 diabetes': 'https://www.nhs.uk/conditions/type-1-diabetes/',
 'Type 2 diabetes': 'https://www.nhs.uk/conditions/type-2-diabetes/',
 'Gestational diabetes': 'https://www.nhs.uk/conditions/gestational-diabetes/'
}

# load_dotenv()

# PG_URL = f"postgresql://{os.getenv('POSTGRES_USER' )} : {os. getenv('POSTGRES_PASSWORD' )}@localhost: 5432/{os.getenv('POSTGRES_DB')}"
# MONGO_URL= "mongodb://localhost:27017/"

# def ingest_structured_data(file_path):
#     engine = create_engine(PG_URL)
#     af = pd.read_csv(file_path)
#     af.to_sql('saude_transacional', engine, if_exists='append', index=False, chunksize=10000)
#     print(f"Inseridos {len(af)} registos no PostgreSQL.")

# def ingest_unstructured_data(json_data):
#     client = MongoClient(MONGO_URL)
#     ab = client['helth_ab']
#     collection = ab['logs_saude']
#     collection.insert_many(json_data)

#     print(f'Inseridos {len(json_data)} documentos no MongoDB. ')


def _get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _extract_intro(soup: BeautifulSoup) -> str:
    main = soup.find("main")
    if not main:
        return ""

    for p in main.find_all("p", recursive=True):
        text = p.get_text(strip=True)
        if len(text) > 40:
            return text

    return ""

def _extract_main_table_rows(soup: BeautifulSoup) -> list[dict[str, str]]:
    table = soup.find("table")
    if not table:
        return []

    rows = []
    for tr in table.find_all("tr"):
        cols = tr.find_all("td")
        if len(cols) < 2:
            continue
        rows.append(
            {
                "tipo_diabetes": cols[0].get_text(strip=True),
                "descricao": cols[1].get_text(strip=True),
            }
        )
    return rows


# def _extract_linked_diabetes_pages(soup: BeautifulSoup, base_url: str) -> dict[str, str]:
#     table = soup.find("table")
#     if not table:
#         return {}

#     links = {}
#     for link in table.select("a[href]"):
#         title = link.get_text(strip=True)
#         href = link.get("href", "")
#         if not title or not href:
#             continue
#         links[title] = urljoin(base_url, href)
#     return links


def _find_section_header(soup: BeautifulSoup, keywords: tuple[str, ...]):
    return soup.find(
        ["h2", "h3"],
        string=lambda text: bool(text)
        and any(keyword.lower() in text.lower() for keyword in keywords),
    )


def _extract_bullet_section(soup: BeautifulSoup, keywords: tuple[str, ...]) -> list[str]:
    header = _find_section_header(soup, keywords)
    if not header:
        return []

    ul = header.find_next(["ul", "ol"])
    if not ul:
        return []

    return [item.get_text(strip=True) for item in ul.find_all("li") if item.get_text(strip=True)]


def _extract_text_section(soup: BeautifulSoup, keywords: tuple[str, ...]) -> str:
    header = _find_section_header(soup, keywords)
    if not header:
        return ""

    paragraph = header.find_next("p")
    return paragraph.get_text(strip=True) if paragraph else ""


def extrair_info_diabetes(url: str) -> dict[str, Any]:
    soup = _get_soup(url)

    return {
        "url": url,
        "sintomas": _extract_bullet_section(
            soup, ("symptom",)
        ),
        "causas": _extract_text_section(
            soup, ("cause", "risk")
        ),
        "complicacoes": _extract_bullet_section(
            soup, ("complication",)
        ),
    }

def ingest_nhs() -> dict[str, Any]:
    try:
        soup = _get_soup(NHS_DIABETES_URL)

        intro = _extract_intro(soup)
        tabela_tipos = _extract_main_table_rows(soup)
        sintomas_gerais = _extract_bullet_section(
            soup, ("symptom",)
        )

        detalhes = {
            tipo: extrair_info_diabetes(url)
            for tipo, url in NHS_NAVIGATING_LINKS.items()
        }

        resultado = {
            "fonte": NHS_DIABETES_URL,
            "capturado_em": datetime.now().isoformat(timespec="seconds"),
            "intro": intro,
            "tipos_diabetes": tabela_tipos,
            "sintomas_gerais": sintomas_gerais,
            "detalhes_por_tipo": detalhes,
        }

        return resultado

    except requests.RequestException as exc:
        print(f"erro no crawler (HTTP): {exc}")
        return {}


def _build_storage_payload(nhs_result: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    mongo_docs: list[dict[str, Any]] = []
    chroma_docs: list[str] = []
    chroma_metadatas: list[dict[str, Any]] = []

    captured_at = nhs_result.get("capturado_em")
    source = nhs_result.get("fonte")

    def append_document(tipo: str, secao: str, texto: str, url: str) -> None:
        cleaned_text = (texto or "").strip()
        if not cleaned_text:
            return

        mongo_docs.append(
            {
                "source": source,
                "capturado_em": captured_at,
                "tipo": tipo,
                "secao": secao,
                "texto": cleaned_text,
                "url": url,
            }
        )

        chroma_docs.append(
            " | ".join(
                [
                    f"tipo: {tipo}",
                    f"secao: {secao}",
                    f"texto: {cleaned_text}",
                    f"url: {url}",
                ]
            )
        )

        chroma_metadatas.append(
            {
                "tipo": tipo,
                "secao": secao,
                "source": source,
                "url": url,
            }
        )

    append_document("geral", "intro", nhs_result.get("intro", ""), NHS_DIABETES_URL)

    for row in nhs_result.get("tipos_diabetes", []):
        tipo = row.get("tipo_diabetes", "desconhecido")
        append_document(tipo, "descricao", row.get("descricao", ""), NHS_DIABETES_URL)

    for symptom in nhs_result.get("sintomas_gerais", []):
        append_document("geral", "sintoma", symptom, NHS_DIABETES_URL)

    for tipo, details in nhs_result.get("detalhes_por_tipo", {}).items():
        detail_url = details.get("url", "")
        for symptom in details.get("sintomas", []):
            append_document(tipo, "sintoma", symptom, detail_url)

        append_document(tipo, "causa", details.get("causas", ""), detail_url)

        for complication in details.get("complicacoes", []):
            append_document(tipo, "complicacao", complication, detail_url)

    return mongo_docs, chroma_docs, chroma_metadatas


def persist_nhs_data(nhs_result: dict[str, Any]) -> dict[str, Any]:
    if not nhs_result:
        return {
            "mongo_inserted": 0,
            "chroma_indexed": 0,
            "log_id": "",
            "status": "skip",
        }

    mongo_docs, chroma_docs, chroma_metadatas = _build_storage_payload(nhs_result)

    mongo_inserted = store_documents_in_mongo(
        mongo_docs,
        collection_name=MONGO_COLLECTION_NHS,
    )
    chroma_indexed = index_documents_in_chroma(
        documents=chroma_docs,
        metadatas=chroma_metadatas,
        collection_name=CHROMA_COLLECTION_NHS,
    )
    log_id = log_event_in_mongo(
        {
            "stage": "nhs_ingestion",
            "status": "completed",
            "source": nhs_result.get("fonte", NHS_DIABETES_URL),
            "mongo_inserted": mongo_inserted,
            "chroma_indexed": chroma_indexed,
        }
    )

    return {
        "mongo_inserted": mongo_inserted,
        "chroma_indexed": chroma_indexed,
        "log_id": log_id,
        "status": "ok",
    }

if __name__ == "__main__":
    result = ingest_nhs()
    persist_result = persist_nhs_data(result)

    print("--- Resultado ingestão NHS ---")
    print(f"Fonte: {result.get('fonte', NHS_DIABETES_URL)}")
    print(f"Capturado em: {result.get('capturado_em', 'N/A')}")
    print(f"MongoDB: {persist_result.get('mongo_inserted', 0)} documentos")
    print(f"ChromaDB: {persist_result.get('chroma_indexed', 0)} embeddings")
    print(f"Log Mongo: {persist_result.get('log_id', '')}")
