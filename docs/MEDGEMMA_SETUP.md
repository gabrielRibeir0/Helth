# Guia de Implementação MedGemma

## 🎯 Visão Geral

O **MedGemma** é uma família de modelos de linguagem especializados em medicina, desenvolvidos pela Google DeepMind. Estão otimizados para tarefas médicas e clínicas.

Este guia cobre a implementação no sistema HELTH com **3 opções de deployment**.

---

## 📋 Pré-requisitos

### Opção 1: Ollama (Recomendado para Início)
- ✅ **Mais Simples**: Setup em 2 minutos
- ✅ **Gratuito**: Deployment local
- ✅ **Bom para**: Desenvolvimento e prototipagem

**Requisitos:**
```bash
# 1. Instalar Ollama
# macOS/Linux: https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Baixar MedGemma
ollama pull medgemma

# 3. Verificar (servidor roda automaticamente em localhost:11434)
ollama list
```

### Opção 2: HuggingFace (Controlo Total)
- ✅ **Flexível**: Deployment local ou cloud
- ✅ **Gratuito**: Modelos open-source
- ⚠️ **Requer**: GPU com ≥8GB VRAM (2B) ou ≥16GB (7B)

**Requisitos:**
```bash
# Instalar dependências
pip install transformers accelerate bitsandbytes torch sentencepiece

# GPU NVIDIA necessária (verificar)
nvidia-smi
```

### Opção 3: Google Vertex AI (Produção Cloud)
- ✅ **Escalável**: Managed service
- ✅ **Sem infraestrutura**: Google gere tudo
- ⚠️ **Pago**: Cobrado por uso

**Requisitos:**
```bash
# 1. Conta GCP ativa
# 2. Vertex AI API ativada
gcloud services enable aiplatform.googleapis.com

# 3. Autenticação
gcloud auth application-default login

# 4. Instalar SDK
pip install langchain-google-vertexai google-cloud-aiplatform
```

---

## 🚀 Instalação

### 1. Clonar/Atualizar Repositório

```bash
cd sns24
git pull  # se já tiver o repositório
```

### 2. Instalar Dependências

Escolha UMA das seguintes opções:

#### Opção A: Ollama (Simples)
```bash
# Dependências base
pip install -e .

# MedGemma via Ollama (já instalado nos pré-requisitos)
ollama pull medgemma
```

#### Opção B: HuggingFace (Local)
```bash
# Todas as dependências (inclui PyTorch, Transformers, etc.)
pip install -e .

# OU instalar apenas extras para HuggingFace
pip install transformers accelerate bitsandbytes torch sentencepiece
```

#### Opção C: Vertex AI (Cloud)
```bash
# Dependências base
pip install -e .

# Extras para Vertex AI
pip install langchain-google-vertexai google-cloud-aiplatform
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env
nano .env
```

Adicionar ao `.env`:
```bash
# LLM Provider (escolher um)
MEDGEMMA_PROVIDER=ollama  # ou "huggingface" ou "vertexai"
MEDGEMMA_MODEL_SIZE=2b    # "2b" ou "7b" (apenas HuggingFace)

# Google Cloud (apenas se MEDGEMMA_PROVIDER=vertexai)
GOOGLE_CLOUD_PROJECT=seu-projeto-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Outras configurações
POSTGRES_USER=helth_user
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=helth_db
```

---

## 💻 Uso Básico

### Teste Rápido (Ollama)

```python
from src.llm.medgemma import get_medgemma_llm

# Criar LLM
llm = get_medgemma_llm(provider="ollama")

# Testar
resposta = llm.invoke("O que é hipertensão arterial?")
print(resposta)
```

### Teste Rápido (HuggingFace)

```python
from src.llm.medgemma import get_medgemma_llm

# Criar LLM (primeira vez demora ~2-5 min para download)
llm = get_medgemma_llm(
    provider="huggingface",
    model_size="2b",  # ou "7b" se tiver GPU potente
    use_quantization=True  # Reduz uso de memória
)

# Testar
resposta = llm.invoke("Quais os sintomas de diabetes tipo 2?")
print(resposta)
```

### Agente Completo

```python
from src.agents.nesy_agent import create_medgemma_agent
from langchain.tools import Tool

# Definir ferramentas
tools = [
    Tool(
        name="ConsultarVitais",
        func=lambda paciente_id: f"PA: 120/80, FC: 72, SpO2: 98%",
        description="Consulta sinais vitais do paciente"
    ),
]

# Criar agente
agent = create_medgemma_agent(
    tools=tools,
    db_postgres=None,  # suas conexões
    vector_db=None,
    mongo_db=None,
    provider="ollama"  # ou "huggingface", "vertexai"
)

# Usar
resposta = agent.query("Consulta vitais do paciente 001 e avalia")
print(resposta)
```

---

## 🎛️ Configurações Avançadas

### Controlo de Temperatura

```python
# Mais conservador (produção médica)
llm = get_medgemma_llm(
    provider="huggingface",
    model_size="7b",
    temperature=0.3  # Respostas mais determinísticas
)

# Mais criativo (exploração)
llm = get_medgemma_llm(
    provider="huggingface",
    model_size="2b",
    temperature=0.9  # Respostas mais variadas
)
```

### Otimização de Memória (HuggingFace)

```python
from src.llm.medgemma import MedGemmaHuggingFace

# Quantização 4-bit (recomendado para GPUs <16GB)
llm = MedGemmaHuggingFace(
    model_name="google/medgemma-7b",
    use_quantization=True,  # Reduz de ~14GB para ~4GB
    device="auto"
)

# Sem quantização (apenas se tiver VRAM suficiente)
llm = MedGemmaHuggingFace(
    model_name="google/medgemma-7b",
    use_quantization=False,
    device="cuda"
)
```

### CPU-only (Lento mas Possível)

```python
llm = get_medgemma_llm(
    provider="huggingface",
    model_size="2b",
    device="cpu",
    use_quantization=True
)
# ⚠️ Aviso: 10-50x mais lento que GPU
```

---

## 📊 Comparação de Opções

| Critério | Ollama | HuggingFace | Vertex AI |
|----------|--------|-------------|-----------|
| **Setup** | ⭐⭐⭐⭐⭐ Simples | ⭐⭐⭐ Médio | ⭐⭐ Complexo |
| **Custo** | 💰 Gratuito | 💰 Gratuito | 💰💰💰 Pago |
| **Velocidade** | ⚡⚡⚡ Rápida | ⚡⚡⚡⚡ Muito rápida | ⚡⚡⚡⚡⚡ Escalável |
| **Controlo** | ⭐⭐ Básico | ⭐⭐⭐⭐⭐ Total | ⭐⭐⭐ Médio |
| **GPU Necessária** | ❌ Não | ✅ Sim (8-16GB) | ❌ Não (cloud) |
| **Internet** | ❌ Não | ❌ Não* | ✅ Sim |
| **Melhor para** | Dev/Prototipagem | Produção local | Produção cloud |

*Após download inicial

---

## 🔧 Troubleshooting

### Problema: "CUDA out of memory"
```python
# Solução: Usar quantização ou modelo menor
llm = get_medgemma_llm(
    provider="huggingface",
    model_size="2b",  # trocar de 7b para 2b
    use_quantization=True
)
```

### Problema: Ollama não conecta
```bash
# Verificar se servidor está a correr
curl http://localhost:11434/api/tags

# Reiniciar Ollama
ollama serve

# Verificar se modelo foi baixado
ollama list
```

### Problema: Download lento (HuggingFace)
```python
# Definir mirror (se fora dos EUA)
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
```

---

## 📚 Recursos Adicionais

- **Documentação MedGemma**: https://deepmind.google/models/gemma/medgemma/
- **HuggingFace Hub**: https://huggingface.co/google/medgemma-2b
- **Ollama**: https://ollama.ai
- **Exemplos de Código**: `/examples/medgemma_usage.py`

---

## 🎓 Próximos Passos

1. ✅ **Testar localmente**: Use Ollama para validar funcionamento
2. ✅ **Adicionar ferramentas**: Criar queries SQL, RAG, calculadoras
3. ✅ **Integrar interface**: Conectar ao Streamlit ([app.py](app.py))
4. ✅ **Deploy produção**: Escolher HuggingFace (local) ou Vertex AI (cloud)

---

**Dúvidas?** Ver exemplos completos em [`examples/medgemma_usage.py`](../examples/medgemma_usage.py)
