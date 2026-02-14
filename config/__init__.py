"""
Configurações do sistema HELTH
"""

from .medgemma_config import (
    MedGemmaConfig,
    DEV_CONFIG,
    DEV_OLLAMA_CONFIG,
    PROD_LOCAL_CONFIG,
    PROD_CLOUD_CONFIG,
)

__all__ = [
    "MedGemmaConfig",
    "DEV_CONFIG",
    "DEV_OLLAMA_CONFIG",
    "PROD_LOCAL_CONFIG",
    "PROD_CLOUD_CONFIG",
]
