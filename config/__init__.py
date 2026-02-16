"""
Configurações do sistema HELTH
"""

from .medgemma_config import (
    DEV_CONFIG,
    DEV_OLLAMA_CONFIG,
    PROD_CLOUD_CONFIG,
    PROD_LOCAL_CONFIG,
    MedGemmaConfig,
)

__all__ = [
    "MedGemmaConfig",
    "DEV_CONFIG",
    "DEV_OLLAMA_CONFIG",
    "PROD_LOCAL_CONFIG",
    "PROD_CLOUD_CONFIG",
]
