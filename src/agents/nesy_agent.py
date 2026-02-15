# from typing import Any, Optional
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain.prompts import ChatPromptTemplate
# from langchain_core.language_models.llms import LLM
# from langchain.tools import Tool
# import logging

# logger = logging.getLogger(__name__)


# class MedicalDecisionAgent:
#     """
#     Agente Neuro-Simbólico para Suporte Médico
    
#     Arquitetura:
#     - Entrada: Pergunta do utilizador
#     - Router (LLM): Decide qual/quais ferramentas usar
#     - Ferramentas (Determinísticas):
#         1. QueryExecutor: SQL/NoSQL
#         2. RAGSearcher: Vector DB
#         3. ClinicalCalculator: Lógica pura
#     - Saída: Resposta contextualizada + Justificação
    
#     Suporta múltiplos LLMs:
#     - MedGemma (recomendado para contexto médico)
#     - OpenAI GPT-4
#     - Azure OpenAI
#     - Outros modelos via LangChain
#     """

#     def __init__(
#         self,
#         llm: LLM,
#         tools: list[Tool],
#         db_postgres: Any,
#         vector_db: Any,
#         mongo_db: Any,
#     ):
#         """
#         Args:
#             llm: Modelo de linguagem (pode ser MedGemma, GPT-4, etc.)
#             tools: Lista de ferramentas disponíveis para o agente
#             db_postgres: Conexão PostgreSQL
#             vector_db: Base de dados vectorial (ChromaDB/FAISS)
#             mongo_db: Conexão MongoDB
#         """
#         self.llm = llm
#         self.tools = tools
#         self.db_postgres = db_postgres
#         self.vector_db = vector_db
#         self.mongo_db = mongo_db
#         self.agent = self._create_agent()

#     def _create_agent(self) -> AgentExecutor:
#         """Cria o agente com tools e prompt configurados"""
#         prompt = ChatPromptTemplate.from_messages([
#             ("system", """És um Assistente Médico Inteligente especializado em Suporte à Decisão Clínica.

#             O TEU PAPEL:
#             - Analisar dados de pacientes (vitais, medicações, histórico)
#             - Consultar guidelines médicos para recomendações
#             - Alertar sobre riscos (interações, valores anómalos)
#             - EXPLICAR a lógica por trás de cada recomendação

#             REGRAS CRÍTICAS:
#             1. Se usou uma ferramenta, SEMPRE explicar o resultado ao utilizador.
#             2. Ser preciso com números e métricas (não aproximar).
#             3. Se não souber, dizer honestamente.
#             4. Citar fontes quando disponível.

#             FLUXO RECOMENDADO:
#             1. Para perguntas de DADOS → Use QueryDatabase
#             2. Para perguntas de CONTEXTO/GUIDELINES → Use RAGSearch
#             3. Para CÁLCULOS clínicos → Use ClinicalCalculator
#             4. Use múltiplas ferramentas se necessário (ex: Query + RAG)

#             Responda sempre em português de portugal.
# """),
#             ("human", "{input}"),
#             ("placeholder", "{agent_scratchpad}"),
#         ])
        
#         agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
#         return AgentExecutor(
#             agent=agent,
#             tools=self.tools,
#             verbose=True,
#             handle_parsing_errors=True,
#             max_iterations=5,
#         )
    
#     def query(self, question: str) -> str:
#         """Executa uma pergunta no agente"""
#         try:
#             response = self.agent.invoke({"input": question})
#             return response.get("output", "")
#         except Exception as e:
#             logger.error(f"Erro na query do agente: {e}")
#             return f"Erro ao processar pergunta: {str(e)}"


# def create_medgemma_agent(
#     tools: list[Tool],
#     db_postgres: Any,
#     vector_db: Any,
#     mongo_db: Any,
#     provider: str = "huggingface",
#     model_size: str = "2b",
#     **kwargs,
# ) -> MedicalDecisionAgent:
#     """
#     Factory function para criar agente com MedGemma
    
#     Args:
#         tools: Ferramentas disponíveis
#         db_postgres: Conexão PostgreSQL
#         vector_db: Vector store
#         mongo_db: Conexão MongoDB
#         provider: "huggingface", "ollama", ou "vertexai"
#         model_size: "2b" ou "7b" (apenas HuggingFace)
#         **kwargs: Argumentos adicionais para o LLM
    
#     Returns:
#         MedicalDecisionAgent configurado com MedGemma
    
#     Exemplo:
#         # Desenvolvimento local (Ollama - mais simples)
#         agent = create_medgemma_agent(
#             tools=my_tools,
#             db_postgres=pg_conn,
#             vector_db=chroma,
#             mongo_db=mongo_conn,
#             provider="ollama"
#         )
        
#         # Produção local (HuggingFace)
#         agent = create_medgemma_agent(
#             tools=my_tools,
#             db_postgres=pg_conn,
#             vector_db=chroma,
#             mongo_db=mongo_conn,
#             provider="huggingface",
#             model_size="7b",
#             use_quantization=False
#         )
#     """
#     from src.llm.medgemma import get_medgemma_llm
    
#     logger.info(f"A criar agente MedGemma (provider={provider}, size={model_size})")
    
#     llm = get_medgemma_llm(
#         provider=provider,
#         model_size=model_size,
#         **kwargs
#     )
    
#     return MedicalDecisionAgent(
#         llm=llm,
#         tools=tools,
#         db_postgres=db_postgres,
#         vector_db=vector_db,
#         mongo_db=mongo_db,
#     )