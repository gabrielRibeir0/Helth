"""
MedGemma LLM Integration
Implementação do modelo MedGemma da Google para suporte à decisão médica.

Opções de deployment:
1. HuggingFace (local/cloud)
2. Google Vertex AI
3. Ollama (local)
"""

import logging
import os

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

logger = logging.getLogger(__name__)


class MedGemmaHuggingFace:
    """
    MedGemma via HuggingFace Transformers

    Requisitos:
    - GPU recomendada (mínimo 8GB VRAM para 2B, 16GB para 7B)
    - CPU possível mas lento
    """

    def __init__(
        self,
        model_name: str = "google/medgemma-2b",
        device: str = "auto",
        max_length: int = 2048,
        temperature: float = 0.7,
        use_quantization: bool = True,
    ):
        """
        Args:
            model_name: "google/medgemma-2b" ou "google/medgemma-7b"
            device: "auto", "cuda", "cpu"
            max_length: Comprimento máximo de geração
            temperature: Controla aleatoriedade (0.0 = determinístico, 1.0 = criativo)
            use_quantization: Reduz uso de memória (recomendado para GPUs <16GB)
        """
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.use_quantization = use_quantization

        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """Carrega modelo e tokenizer"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            logger.info(f"A carregar MedGemma: {self.model_name}")

            # Configuração de quantização (4-bit) para reduzir memória
            quantization_config = None
            if self.use_quantization:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    # Melhora precisão em modelos menores
                    bnb_4bit_quant_type="nf4"
                )

            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                # Necessário para modelos personalizados como MedGemma para carregar
                # corretamente os tokenizers específicos do modelo
            )

            # Carregar modelo
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map=self.device,
                trust_remote_code=True,
                # Necessário para modelos personalizados como MedGemma para carregar
                # corretamente os modelos específicos do modelo
                torch_dtype=torch.float16 if not self.use_quantization else None
            )

            logger.info(f"✓ MedGemma carregado com sucesso em {self.device}")

        except ImportError as e:
            raise ImportError(
                "Dependências em falta. Instalar com:\n"
                "pip install transformers accelerate bitsandbytes torch"
            ) from e
        except Exception as e:
            logger.error(f"Erro ao carregar MedGemma: {e}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Gera resposta do modelo

        Args:
            prompt: Texto de entrada
            **kwargs: Parâmetros adicionais (max_new_tokens, temperature, etc.)

        Returns:
            Texto gerado
        """
        import torch

        # Preparar input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # Parâmetros de geração
        gen_kwargs = {
            "max_new_tokens": kwargs.get("max_new_tokens", 512),
            "temperature": kwargs.get("temperature", self.temperature),
            "do_sample": kwargs.get("do_sample", True),
            # Habilitar amostragem para respostas mais variadas
            "top_p": kwargs.get("top_p", 0.9),
            # Nucleus sampling para controlar diversidade
            "top_k": kwargs.get("top_k", 50),
            # Top-k sampling para controlar diversidade
            "pad_token_id": self.tokenizer.eos_token_id,
            # Garantir que o modelo saiba quando parar
        }

        # Gerar
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        # Decodificar (remover prompt original)
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()


class MedGemmaLangChain(LLM):
    """
    Wrapper LangChain para MedGemma
    Permite usar MedGemma como qualquer outro LLM do LangChain
    """

    medgemma: MedGemmaHuggingFace

    def __init__(self, **kwargs):
        super().__init__()
        self.medgemma = MedGemmaHuggingFace(**kwargs)

    @property
    def _llm_type(self) -> str:
        return "medgemma"

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs,
    ) -> str:
        """Executa o modelo"""
        response = self.medgemma.generate(prompt, **kwargs)

        # Aplicar stop sequences se fornecidas
        if stop:
            for stop_seq in stop:
                if stop_seq in response:
                    response = response.split(stop_seq)[0]

        return response


class MedGemmaOllama:
    """
    MedGemma via Ollama (deployment local simplificado)

    Setup:
    1. Instalar Ollama: https://ollama.ai
    2. Executar: ollama pull medgemma
    3. Usar este wrapper
    """

    def __init__(self, model_name: str = "medgemma", base_url: str = "http://localhost:11434"):
        """
        Args:
            model_name: Nome do modelo no Ollama
            base_url: URL do servidor Ollama
        """
        try:
            from langchain_community.llms import Ollama

            self.llm = Ollama(
                model=model_name,
                base_url=base_url,
                temperature=0.7,
            )
            logger.info(f"✓ MedGemma Ollama conectado: {base_url}")
        except ImportError as err:
            raise ImportError("Instalar: pip install langchain-community") from err

    def get_llm(self):
        """Retorna instância LangChain"""
        return self.llm


class MedGemmaVertexAI:
    """
    MedGemma via Google Vertex AI (produção escalável)

    Setup:
    1. Configurar projeto GCP
    2. Ativar Vertex AI API
    3. Autenticar: gcloud auth application-default login
    4. Definir variáveis de ambiente
    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str = "us-central1",
        model_name: str = "medgemma-2b",
    ):
        """
        Args:
            project_id: ID do projeto GCP (ou usar GOOGLE_CLOUD_PROJECT env var)
            location: Região GCP
            model_name: Nome do modelo MedGemma
        """
        try:
            from langchain_google_vertexai import VertexAI

            self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
            if not self.project_id:
                raise ValueError("project_id necessário ou definir GOOGLE_CLOUD_PROJECT")

            self.llm = VertexAI(
                model_name=model_name,
                project=self.project_id,
                location=location,
                temperature=0.7,
                max_output_tokens=1024,
            )
            logger.info(f"✓ MedGemma Vertex AI conectado: {self.project_id}")
        except ImportError as err:
            raise ImportError("Instalar: pip install langchain-google-vertexai") from err

    def get_llm(self):
        """Retorna instância LangChain"""
        return self.llm


def get_medgemma_llm(
    provider: str = "huggingface",
    model_size: str = "2b",
    **kwargs
) -> LLM:
    """
    Factory function para criar instância MedGemma

    Args:
        provider: "huggingface", "ollama", ou "vertexai"
        model_size: "2b" ou "7b" (apenas para huggingface)
        **kwargs: Parâmetros específicos do provider

    Returns:
        Instância LangChain LLM

    Exemplo:
        # HuggingFace (local)
        llm = get_medgemma_llm("huggingface", model_size="2b")

        # Ollama (local simplificado)
        llm = get_medgemma_llm("ollama")

        # Vertex AI (produção)
        llm = get_medgemma_llm("vertexai", project_id="meu-projeto")
    """
    if provider == "huggingface":
        model_name = kwargs.pop("model_name", f"google/medgemma-{model_size}")
        return MedGemmaLangChain(model_name=model_name, **kwargs)

    elif provider == "ollama":
        return MedGemmaOllama(**kwargs).get_llm()

    elif provider == "vertexai":
        return MedGemmaVertexAI(**kwargs).get_llm()

    else:
        raise ValueError(
            f"Provider desconhecido: {provider}. Use 'huggingface', "
            "'ollama', ou 'vertexai'"
        )
