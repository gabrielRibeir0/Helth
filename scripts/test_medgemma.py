#!/usr/bin/env python3
"""
Script de Teste para MedGemma
Verifica se o MedGemma está configurado corretamente
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_ollama():
    """Testa MedGemma via Ollama"""
    logger.info("🧪 Testando MedGemma via Ollama...")
    
    try:
        from src.llm.medgemma import get_medgemma_llm
        
        llm = get_medgemma_llm(provider="ollama")
        resposta = llm.invoke("O que é hipertensão arterial? Responda em 2 frases.")
        
        logger.info("✅ Ollama funcionando!")
        logger.info(f"📝 Resposta: {resposta[:200]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no Ollama: {e}")
        logger.info("💡 Certifica-te que:")
        logger.info("   1. Ollama está instalado: https://ollama.ai")
        logger.info("   2. Modelo foi baixado: ollama pull medgemma")
        logger.info("   3. Servidor está a correr: ollama serve")
        return False


def test_huggingface():
    """Testa MedGemma via HuggingFace"""
    logger.info("🧪 Testando MedGemma via HuggingFace...")
    
    try:
        from src.llm.medgemma import get_medgemma_llm
        
        logger.info("⏳ A carregar modelo (primeira vez pode demorar ~5 min)...")
        llm = get_medgemma_llm(
            provider="huggingface",
            model_size="2b",
            use_quantization=True
        )
        
        resposta = llm.invoke("O que é diabetes? Uma frase.")
        
        logger.info("✅ HuggingFace funcionando!")
        logger.info(f"📝 Resposta: {resposta[:200]}...")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Dependências em falta: {e}")
        logger.info("💡 Instalar com: pip install transformers accelerate bitsandbytes torch")
        return False
    except Exception as e:
        logger.error(f"❌ Erro no HuggingFace: {e}")
        logger.info("💡 Certifica-te que:")
        logger.info("   1. GPU disponível (ou use device='cpu')")
        logger.info("   2. Drivers CUDA instalados (se usar GPU)")
        return False


def test_config():
    """Testa se as configurações estão corretas"""
    logger.info("🧪 Testando configurações...")
    
    try:
        from config import DEV_CONFIG, DEV_OLLAMA_CONFIG
        
        logger.info(f"✅ Config DEV: provider={DEV_CONFIG.provider}, size={DEV_CONFIG.model_size}")
        logger.info(f"✅ Config OLLAMA: provider={DEV_OLLAMA_CONFIG.provider}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas configurações: {e}")
        return False


def check_dependencies():
    """Verifica dependências instaladas"""
    logger.info("🔍 Verificando dependências...")
    
    deps = {
        "langchain": "langchain",
        "langchain_core": "langchain-core",
        "transformers": "transformers (opcional - HuggingFace)",
        "torch": "torch (opcional - HuggingFace)",
    }
    
    for module, desc in deps.items():
        try:
            __import__(module)
            logger.info(f"  ✅ {desc}")
        except ImportError:
            logger.warning(f"  ⚠️  {desc} - não instalado")


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🏥 TESTE DE CONFIGURAÇÃO MEDGEMMA - HELTH")
    print("=" * 60)
    print()
    
    # 1. Verificar dependências
    check_dependencies()
    print()
    
    # 2. Testar configurações
    test_config()
    print()
    
    # 3. Perguntar qual provider testar
    print("Qual provider deseja testar?")
    print("1. Ollama (recomendado)")
    print("2. HuggingFace (requer GPU)")
    print("3. Ambos")
    print("0. Sair")
    
    try:
        escolha = input("\nEscolha (1/2/3/0): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelado pelo utilizador")
        return
    
    print()
    
    if escolha == "1":
        success = test_ollama()
    elif escolha == "2":
        success = test_huggingface()
    elif escolha == "3":
        success_ollama = test_ollama()
        print()
        success_hf = test_huggingface()
        success = success_ollama or success_hf
    elif escolha == "0":
        logger.info("👋 Até breve!")
        return
    else:
        logger.error("❌ Opção inválida")
        return
    
    print()
    print("=" * 60)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("🎉 MedGemma pronto a usar no HELTH")
        print()
        print("📚 Próximos passos:")
        print("   - Ver exemplos: examples/medgemma_usage.py")
        print("   - Ler documentação: docs/MEDGEMMA_SETUP.md")
    else:
        print("❌ TESTE FALHOU")
        print("🔧 Ver mensagens de erro acima para resolver problemas")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
