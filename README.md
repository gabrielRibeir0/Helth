# Helth

## Semana 4: Persistência

## ADR (Architecture Decision Records)

- Índice ADR: [docs/adr/README.md](docs/adr/README.md)
- Primeiro registo: [docs/adr/0001-arquitetura-persistencia.md](docs/adr/0001-arquitetura-persistencia.md)

### 1) Levantar bases de dados no Docker

```sh
cp .env.example .env
docker compose up -d postgres mongo chromadb
```

### 2) Pipeline ETL para SQL (dados estruturados)

O ETL está implementado em `src/persistence/week4_persistence.py` na função `etl_csv_to_postgres`, que:

- extrai de CSV,
- transforma (normalização de colunas/valores),
- carrega no PostgreSQL (tabela `saude_transacional`).

### 3) Armazenamento NoSQL (documentos/logs)

Implementado no mesmo módulo:

- `store_documents_in_mongo` para documentos de dataset;
- `log_event_in_mongo` para eventos/logs de pipeline.

### 4) Embeddings + DB Vetorial (Chroma)

Implementado com `DefaultEmbeddingFunction` do Chroma (modelo ONNX MiniLM-L6-v2) na função `index_documents_in_chroma`.

- coleção default: `helth_embeddings`;
- Chroma via `HttpClient` (`CHROMA_HOST`/`CHROMA_PORT`).

### 5) Teste de integração (SQL + NoSQL + Vetorial)

Executar:

```sh
python scripts/test_persistence_integration.py
```

O script valida conectividade aos 3 bancos e faz escrita real em:

- PostgreSQL: tabela `saude_transacional`;
- MongoDB: coleções `dataset_documentos` e `pipeline_logs`;
- Chroma: coleção `helth_embeddings`.

## Contribuir

- Verificação do código

`ruff check`

- Corrigir erros

`ruff check --fix`

- Fazer pull request

```sh
git checkout -b nome-branch

git add .
git commit -m "<msg>"

git push -u origin nome-branch
```

- Apagar branch local (e remoto no Github)

```sh
git checkout main
git branch -d nome-branch
```
