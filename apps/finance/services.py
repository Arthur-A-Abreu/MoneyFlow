import json
import logging
from django.conf import settings
from apps.finance.schemas import ExtratoSchema

logger = logging.getLogger(__name__)

# Modelos em ordem de preferência para fallback automático
GEMINI_MODELS_FALLBACK = [
    'gemini-3.5-flash',
    'gemini-flash-latest',
    'gemini-3.6-flash',
    'gemini-3.7-flash',
    'gemini-3.1-flash-lite',
    'gemini-3.8-flash',
]


def process_statement_with_gemini(file_bytes: bytes, mime_type: str, user_categories: list[str] = None) -> dict:
    """
    Envia os bytes de um extrato/fatura (PDF, PNG, JPG ou WEBP) para a API do Google Gemini
    utilizando a SDK oficial google-genai com saídas estruturadas (Pydantic).

    Tenta automaticamente múltiplos modelos em ordem de fallback caso algum
    esteja sobrecarregado ou indisponível.

    Retorna um dicionário no formato:
    {
        "transacoes": [
            {
                "data": "2026-09-10",
                "descricao": "Supermercado Carrefour",
                "valor": 150.50,
                "tipo": "despesa",
                "categoria": "Alimentação"
            }, ...
        ]
    }
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or getattr(settings, 'GOOGLE_API_KEY', None)
    if not api_key:
        raise ValueError("Chave de API do Gemini (GEMINI_API_KEY) não configurada no arquivo .env.")

    categories_hint = ""
    if user_categories:
        categories_hint = (
            f"Tente mapear a categoria das transações para uma destas categorias cadastradas "
            f"do usuário se for adequado: {', '.join(user_categories)}."
        )

    prompt = f"""
    Você é um assistente financeiro especialista em leitura e extração de dados de faturas de cartão de crédito e extratos bancários.
    Analise o documento fornecido em anexo e extraia todas as transações financeiras individuais encontradas.

    Regras Estritas de Extração:
    1. Data: extraia a data de cada transação no formato exato YYYY-MM-DD.
    2. Descrição: nome limpo do estabelecimento ou histórico (ex: "Supermercado Carrefour", "Uber", "Pix Recebido").
    3. Valor: número decimal positivo (ex: 49.90).
    4. Tipo: utilize estritamente "despesa" (para compras, pagamentos, saídas) ou "receita" (para créditos, salários, PIX recebidos).
    5. Categoria: {categories_hint} Se nenhuma se encaixar perfeitamente, atribua uma categoria adequada em português (ex: Alimentação, Transporte, Moradia, Lazer, Saúde, Outros).
    6. Se o arquivo não contiver um extrato ou fatura válida, retorne uma lista de transações vazia.
    """

    # 1. Tenta com a SDK oficial `google-genai`
    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import ClientError, ServerError

        client = genai.Client(api_key=api_key)
        last_error = None

        for model_name in GEMINI_MODELS_FALLBACK:
            try:
                logger.info(f"Tentando modelo Gemini: {model_name}")

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ExtratoSchema,
                        temperature=0.1,
                    )
                )

                logger.info(f"Processamento concluído com modelo: {model_name}")
                if hasattr(response, 'parsed') and response.parsed:
                    return response.parsed.model_dump()
                elif hasattr(response, 'text') and response.text:
                    return json.loads(response.text)

            except (ClientError, ServerError) as model_err:
                status_code = getattr(model_err, 'status_code', None) or getattr(model_err, 'code', 0)
                logger.warning(f"Modelo {model_name} indisponível (código {status_code}): {model_err}. Tentando próximo...")
                last_error = model_err
                continue
            except Exception as model_err:
                logger.warning(f"Erro inesperado com modelo {model_name}: {model_err}. Tentando próximo...")
                last_error = model_err
                continue

        raise RuntimeError(
            f"Nenhum modelo Gemini disponível no momento. Último erro: {last_error}\n"
            f"Modelos tentados: {', '.join(GEMINI_MODELS_FALLBACK)}"
        )

    except ImportError:
        logger.warning("google-genai não encontrada. Usando fallback legado...")

    # 2. Fallback para `google.generativeai` (biblioteca legada caso presente)
    try:
        import google.generativeai as genai_legacy

        genai_legacy.configure(api_key=api_key)
        last_error = None

        for model_name in GEMINI_MODELS_FALLBACK:
            try:
                logger.info(f"[Legado] Tentando modelo: {model_name}")
                model = genai_legacy.GenerativeModel(model_name)

                part = {'mime_type': mime_type, 'data': file_bytes}
                full_prompt = f"{prompt}\nResponda APENAS em JSON no formato: {ExtratoSchema.model_json_schema()}"
                response = model.generate_content([part, full_prompt])

                cleaned_text = response.text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]

                return json.loads(cleaned_text.strip())

            except Exception as model_err:
                logger.warning(f"[Legado] Modelo {model_name} falhou: {model_err}. Tentando próximo...")
                last_error = model_err
                continue

        raise RuntimeError(f"Todos os modelos Gemini falharam. Último erro: {last_error}")

    except Exception as e:
        logger.error(f"Erro final no processamento Gemini: {e}")
        raise RuntimeError(f"Erro ao processar documento com IA Gemini: {str(e)}")
