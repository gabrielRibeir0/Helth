from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

NHS_DIABETES_URL = "https://www.nhs.uk/conditions/diabetes/"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 20
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

if __name__ == "__main__":
    ingest_nhs()
