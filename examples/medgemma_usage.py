# """
# Exemplos de Uso do MedGemma no HELTH

# Este ficheiro demonstra as diferentes formas de inicializar e usar o MedGemma.
# """

# import logging
# from langchain.tools import Tool

# # Configurar logging
# logging.basicConfig(level=logging.INFO)


# # =============================================================================
# # EXEMPLO 1: MedGemma via Ollama (Mais Simples - Recomendado para Desenvolvimento)
# # =============================================================================

# def exemplo_ollama():
#     """
#     Setup mais simples para desenvolvimento local.
    
#     Requisitos:
#     1. Instalar Ollama: https://ollama.ai
#     2. Executar no terminal: ollama pull medgemma
#     3. Servidor Ollama fica em http://localhost:11434
#     """
#     from src.llm.medgemma import get_medgemma_llm
#     from src.agents.nesy_agent import create_medgemma_agent
    
#     # Criar LLM
#     llm = get_medgemma_llm(provider="ollama")
    
#     # Testar diretamente
#     resposta = llm.invoke("O que é hipertensão arterial?")
#     print(f"MedGemma: {resposta}")
    
#     # Ou usar no agente (precisa de tools e DBs configuradas)
#     # agent = create_medgemma_agent(
#     #     tools=[],  # suas ferramentas
#     #     db_postgres=None,
#     #     vector_db=None,
#     #     mongo_db=None,
#     #     provider="ollama"
#     # )
#     # response = agent.query("Paciente com pressão 160/100. O que fazer?")
#     # print(response)


# # =============================================================================
# # EXEMPLO 2: MedGemma via HuggingFace (Controlo Total)
# # =============================================================================

# def exemplo_huggingface_basico():
#     """
#     Deployment local com HuggingFace.
    
#     Requisitos:
#     - GPU com mínimo 8GB VRAM (para 2B) ou 16GB (para 7B)
#     - pip install transformers accelerate bitsandbytes torch
#     """
#     from src.llm.medgemma import get_medgemma_llm
    
#     # Modelo pequeno (2B) com quantização (para GPUs <16GB)
#     llm = get_medgemma_llm(
#         provider="huggingface",
#         model_size="2b",
#         use_quantization=True,  # Usa 4-bit quantização
#         temperature=0.7,
#     )
    
#     # Testar
#     resposta = llm.invoke("Quais são os sintomas de diabetes tipo 2?")
#     print(f"MedGemma: {resposta}")


# def exemplo_huggingface_avancado():
#     """
#     Configuração avançada para produção local
#     """
#     from src.llm.medgemma import MedGemmaHuggingFace, MedGemmaLangChain
    
#     # Opção 1: Usar diretamente a classe
#     medgemma = MedGemmaHuggingFace(
#         model_name="google/medgemma-7b",  # Modelo maior
#         device="cuda",  # Forçar GPU
#         use_quantization=False,  # Sem quantização (se tiver VRAM suficiente)
#         temperature=0.5,  # Mais conservador para produção
#         max_length=4096,
#     )
    
#     resposta = medgemma.generate(
#         "Paciente com glicemia 280 mg/dL, HbA1c 9.2%. Qual o protocolo?",
#         max_new_tokens=512,
#         temperature=0.3,  # Override para esta query específica
#     )
#     print(f"MedGemma: {resposta}")
    
#     # Opção 2: Wrapper LangChain para usar com chains/agents
#     llm = MedGemmaLangChain(
#         model_name="google/medgemma-7b",
#         device="cuda",
#         use_quantization=False,
#     )
    
#     # Usar em chain
#     from langchain.prompts import PromptTemplate
#     from langchain.chains import LLMChain
    
#     prompt = PromptTemplate(
#         input_variables=["sintomas"],
#         template="Paciente apresenta: {sintomas}\n\nDiagnósticos diferenciais possíveis:"
#     )
    
#     chain = LLMChain(llm=llm, prompt=prompt)
#     resultado = chain.run(sintomas="febre 38.5°C, tosse seca, dispneia, SpO2 92%")
#     print(f"Diagnósticos: {resultado}")


# # =============================================================================
# # EXEMPLO 3: MedGemma via Google Vertex AI (Produção Cloud)
# # =============================================================================

# def exemplo_vertexai():
#     """
#     Deployment em produção com Google Cloud.
    
#     Requisitos:
#     1. Conta GCP com Vertex AI ativado
#     2. gcloud auth application-default login
#     3. export GOOGLE_CLOUD_PROJECT="seu-projeto-id"
#     4. pip install langchain-google-vertexai google-cloud-aiplatform
#     """
#     from src.llm.medgemma import get_medgemma_llm
    
#     llm = get_medgemma_llm(
#         provider="vertexai",
#         project_id="seu-projeto-gcp",  # ou usar env var GOOGLE_CLOUD_PROJECT
#         location="us-central1",
#     )
    
#     resposta = llm.invoke("Protocolo de sepse em adultos?")
#     print(f"MedGemma: {resposta}")


# # =============================================================================
# # EXEMPLO 4: Agente Completo com MedGemma + Tools
# # =============================================================================

# def exemplo_agente_completo():
#     """
#     Exemplo de agente médico completo com ferramentas
#     """
#     from src.agents.nesy_agent import create_medgemma_agent
    
#     # 1. Definir ferramentas (simplificado para exemplo)
#     def calcular_imc(peso: float, altura: float) -> str:
#         """Calcula o Índice de Massa Corporal"""
#         imc = peso / (altura ** 2)
#         categoria = (
#             "Baixo peso" if imc < 18.5
#             else "Peso normal" if imc < 25
#             else "Sobrepeso" if imc < 30
#             else "Obesidade"
#         )
#         return f"IMC: {imc:.1f} ({categoria})"
    
#     def query_vitais(paciente_id: str) -> str:
#         """Consulta sinais vitais do paciente (mock)"""
#         # Aqui seria query real ao PostgreSQL
#         return "PA: 140/90 mmHg, FC: 85 bpm, Temp: 36.7°C, SpO2: 97%"
    
#     tools = [
#         Tool(
#             name="CalcularIMC",
#             func=lambda x: calcular_imc(*map(float, x.split(","))),
#             description="Calcula IMC. Input: 'peso,altura' ex: '70,1.75'"
#         ),
#         Tool(
#             name="QueryVitais",
#             func=query_vitais,
#             description="Consulta sinais vitais. Input: ID do paciente"
#         ),
#     ]
    
#     # 2. Criar agente (usando Ollama para simplicidade)
#     agent = create_medgemma_agent(
#         tools=tools,
#         db_postgres=None,  # Suas conexões reais aqui
#         vector_db=None,
#         mongo_db=None,
#         provider="ollama"  # ou "huggingface", "vertexai"
#     )
    
#     # 3. Fazer perguntas
#     perguntas = [
#         "Qual o IMC de um paciente com 85kg e 1.70m?",
#         "Consulta os vitais do paciente PAC001 e avalia se está tudo normal",
#         "O que significa uma pressão arterial de 140/90?",
#     ]
    
#     for pergunta in perguntas:
#         print(f"\n{'='*60}")
#         print(f"PERGUNTA: {pergunta}")
#         print(f"{'='*60}")
#         resposta = agent.query(pergunta)
#         print(f"RESPOSTA: {resposta}\n")


# # =============================================================================
# # EXEMPLO 5: Comparação de Configurações
# # =============================================================================

# def exemplo_comparacao_configs():
#     """
#     Demonstra diferentes configurações pré-definidas
#     """
#     from config import DEV_CONFIG, DEV_OLLAMA_CONFIG, PROD_LOCAL_CONFIG
#     from src.llm.medgemma import get_medgemma_llm
    
#     # Desenvolvimento (Ollama)
#     print("=== Configuração: Desenvolvimento (Ollama) ===")
#     llm_dev = get_medgemma_llm(**DEV_OLLAMA_CONFIG.to_dict())
    
#     # Desenvolvimento (HuggingFace)
#     print("\n=== Configuração: Desenvolvimento (HuggingFace) ===")
#     llm_dev_hf = get_medgemma_llm(**DEV_CONFIG.to_dict())
    
#     # Produção Local
#     print("\n=== Configuração: Produção Local ===")
#     llm_prod = get_medgemma_llm(**PROD_LOCAL_CONFIG.to_dict())


# # =============================================================================
# # MAIN: Executar Exemplos
# # =============================================================================

# if __name__ == "__main__":
#     print("Exemplos de Uso do MedGemma\n")
    
#     # Descomentar o exemplo que quiser testar:
    
#     # exemplo_ollama()  # Mais simples
#     # exemplo_huggingface_basico()
#     # exemplo_huggingface_avancado()
#     # exemplo_vertexai()
#     # exemplo_agente_completo()
#     # exemplo_comparacao_configs()
    
#     print("\nPara executar um exemplo, descomente a função no main()")
