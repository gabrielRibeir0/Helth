# ADR 0001: Arquitetura de Persistência (PostgreSQL + MongoDB + ChromaDB)

- **Estado:** Aceite
- **Data:** 2026-02-19

## Contexto

O projeto Helth precisa de suportar simultaneamente:

1. dados tabulares estruturados para análise e ETL;
2. documentos semiestruturados e logs operacionais;
3. pesquisa semântica para RAG através de embeddings.

Além disso, a equipa pretende execução local com Docker para desenvolvimento e testes de integração.

## Decisão

Adotar uma arquitetura de persistência poliglota com:

- **PostgreSQL** para dados estruturados e carga ETL;
- **MongoDB** para documentos e logging de pipeline;
- **ChromaDB** para armazenamento vetorial de embeddings.

## Opções consideradas

### Opção A: Apenas PostgreSQL

- **Prós:** simplicidade operacional e menor número de serviços.
- **Contras:** fraco ajuste para documentos flexíveis e capacidades vetoriais menos naturais no contexto atual do projeto.

### Opção B: Apenas MongoDB

- **Prós:** flexibilidade de esquema para dados heterogéneos.
- **Contras:** menor adequação para ETL tabular relacional e governança de dados estruturados.

### Opção C: PostgreSQL + MongoDB + ChromaDB (**escolhida**)

- **Prós:** melhor ajuste por tipo de dado e por caso de uso (SQL, documentos, vetorial).
- **Contras:** maior complexidade operacional e mais componentes para observabilidade.

## Consequências

### Positivas

- melhor separação de responsabilidades por tipo de persistência;
- pipeline de dados mais alinhado com necessidades de IA (RAG);
- validação de integração entre 3 bases já suportada por script de teste.

### Negativas / Trade-offs

- maior custo de manutenção (configuração, monitorização e troubleshooting);
- necessidade de disciplina na consistência de esquemas/metadados entre stores.

## Implementação relacionada

- ETL SQL: `src/persistence/week4_persistence.py` (`etl_csv_to_postgres`)
- NoSQL: `src/persistence/week4_persistence.py` (`store_documents_in_mongo`, `log_event_in_mongo`)
- Vetorial: `src/persistence/week4_persistence.py` (`index_documents_in_chroma`)
- Integração: `scripts/test_persistence_integration.py`
- Containers: `docker-compose.yml`
