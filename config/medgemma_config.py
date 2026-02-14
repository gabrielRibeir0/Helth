"""
Configuração MedGemma
Adaptar conforme necessidades e recursos disponíveis
"""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass
class MedGemmaConfig:
    """Configuração para deployment do MedGemma"""
    
    # Provider: "huggingface", "ollama", "vertexai"
    provider: Literal["huggingface", "ollama", "vertexai"] = "huggingface"
    
    # Modelo (para HuggingFace)
    model_size: Literal["2b", "7b"] = "2b"  # 2B mais rápido, 7B mais preciso
    
    # Device
    device: str = "auto"  # "auto", "cuda", "cpu"
    
    # Quantização (reduz uso de memória)
    use_quantization: bool = True  # Recomendado se GPU <16GB
    
    # Parâmetros de geração
    temperature: float = 0.7  # 0.0-1.0 (menor = mais conservador)
    max_length: int = 2048
    top_p: float = 0.9
    top_k: int = 50
    
    # Vertex AI (se provider="vertexai")
    gcp_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    gcp_location: str = "us-central1"
    
    # Ollama (se provider="ollama")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "medgemma"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "provider": self.provider,
            "model_size": self.model_size,
            "device": self.device,
            "use_quantization": self.use_quantization,
            "temperature": self.temperature,
            "max_length": self.max_length,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }


# Configurações pré-definidas

# Desenvolvimento Local (GPU pequena ou CPU)
DEV_CONFIG = MedGemmaConfig(
    provider="huggingface",
    model_size="2b",
    use_quantization=True,
    temperature=0.7,
)

# Desenvolvimento Local com Ollama (mais simples)
DEV_OLLAMA_CONFIG = MedGemmaConfig(
    provider="ollama",
    temperature=0.7,
)

# Produção Local (GPU potente)
PROD_LOCAL_CONFIG = MedGemmaConfig(
    provider="huggingface",
    model_size="7b",
    use_quantization=False,
    temperature=0.5,  # Mais conservador para produção
)

# Produção Cloud (Vertex AI)
PROD_CLOUD_CONFIG = MedGemmaConfig(
    provider="vertexai",
    temperature=0.5,
)
