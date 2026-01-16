import os
import re
from typing import Dict

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# --- Configuração do Vertex AI (reutilizada do ambiente) ---

MODEL_NAME = "gemini-2.5-flash"  # Modelo rápido e eficiente para geração de texto curto

# --- Estrutura de Prompts para Geração de Resposta ---

# O prompt base define o papel da IA, o tom, as restrições de segurança e os placeholders
# para o conteúdo específico da categoria e do e-mail.
BASE_PROMPT = """
Você é um assistente de e-mail corporativo para uma empresa do setor financeiro.
Sua única tarefa é redigir uma resposta curta e profissional para um e-mail que já foi analisado.

REGRAS DE TOM E ESTILO (OBRIGATÓRIO):
- Seja sempre educado, profissional e objetivo.
- Use uma linguagem clara e direta.
- NÃO use informalidade (gírias, abreviações).
- NÃO use jargões técnicos.
- NÃO use emojis.
- NUNCA prometa ações ou prazos que não estejam explicitamente instruídos.

RESTRIÇÕES DE SEGURANÇA (OBRIGATÓRIAS):
- NÃO invente informações.
- NÃO inclua detalhes do e-mail original na resposta.
- Sua resposta deve ser autossuficiente e genérica.

INSTRUÇÕES PARA ESTA TAREFA ESPECÍFICA:
<<<CATEGORY_INSTRUCTIONS>>>

E-MAIL ORIGINAL (apenas para contexto, não para ser citado):
---
<<<EMAIL_TEXT>>>
---

Gere apenas o texto da resposta, sem introduções ou despedidas adicionais.
"""

# Prompts específicos por categoria, que serão injetados no prompt base.
CATEGORY_PROMPTS = {
    "Produtivo": """
    INSTRUÇÃO: O e-mail foi classificado como "Produtivo".
    OBJETIVO: Redija uma resposta que confirme o recebimento e indique que a solicitação foi registrada e será processada pela equipe responsável.

    EXEMPLO DE RESPOSTA IDEAL:
    "Agradecemos o seu contato. Sua solicitação foi recebida e encaminhada para a equipe responsável. Entraremos em contato se informações adicionais forem necessárias."
    """,
    "Improdutivo": """
    INSTRUÇÃO: O e-mail foi classificado como "Improdutivo".
    OBJETIVO: Redija uma resposta curta e cordial informando que a mensagem foi recebida e que nenhuma ação adicional é necessária.

    EXEMPLO DE RESPOSTA IDEAL:
    "Agradecemos o seu contato. Esta é uma mensagem informativa e nenhuma ação adicional é necessária de nossa parte."
    """
}

# --- Erros Personalizados ---

class InvalidGeneratedResponseError(ValueError):
    """Lançado quando a resposta gerada pela IA falha nas validações de qualidade."""
    pass


# --- Funções Auxiliares de Validação ---

def _validate_generated_response(response_text: str, original_text: str) -> None:
    """
    Executa validações de segurança e qualidade na resposta gerada pela IA.

    Args:
        response_text: O texto da resposta gerada.
        original_text: O texto do e-mail original para verificação de repetição.

    Raises:
        InvalidGeneratedResponseError: Se qualquer validação falhar.
    """
    # 1. Validação de conteúdo vazio ou muito curto
    if not response_text or len(response_text.strip()) < 20:
        raise InvalidGeneratedResponseError("A resposta gerada está vazia ou é muito curta.")

    # 2. Validação de comprimento máximo (evita respostas excessivamente longas)
    if len(response_text) > 1000:
        raise InvalidGeneratedResponseError("A resposta gerada excede o limite de 1000 caracteres.")

    # 3. Validação de frases proibidas (indicam que a IA "quebrou o personagem")
    forbidden_phrases = ["como modelo de linguagem", "não consigo", "não posso"]
    if any(phrase in response_text.lower() for phrase in forbidden_phrases):
        raise InvalidGeneratedResponseError(f"A resposta gerada contém uma frase proibida: '{response_text}'")

    # 4. Validação de repetição (simples)
    # Verifica se a IA não está apenas repetindo uma grande parte do e-mail original.
    if original_text[:100].lower() in response_text.lower() and len(original_text) > 100:
        raise InvalidGeneratedResponseError("A resposta gerada parece repetir o conteúdo do e-mail original.")


# --- Serviço de Geração de Resposta ---

def generate_response(email_text: str, category: str) -> str:
    """
    Gera uma resposta automática para um e-mail com base em sua categoria.

    Args:
        email_text: O conteúdo de texto do e-mail original.
        category: A categoria pré-classificada ("Produtivo" ou "Improdutivo").

    Returns:
        Uma string contendo a resposta gerada e validada.

    Raises:
        ValueError: Se a categoria for desconhecida.
        InvalidGeneratedResponseError: Se a resposta gerada falhar nas validações.
        Exception: Para erros gerais da API Vertex AI.
    """
    if category not in CATEGORY_PROMPTS:
        raise ValueError(f"Categoria de resposta desconhecida: '{category}'")

    # 1. Selecionar e montar o prompt final
    category_instructions = CATEGORY_PROMPTS[category]
    prompt = BASE_PROMPT.replace("<<<CATEGORY_INSTRUCTIONS>>>", category_instructions)
    prompt = prompt.replace("<<<EMAIL_TEXT>>>", email_text)

    # 2. Chamar a API do Gemini via Vertex AI
    model = GenerativeModel(MODEL_NAME)
    generation_config = GenerationConfig(
        temperature=0.1,  # Baixa temperatura para manter a consistência e o tom
        max_output_tokens=256
    )

    response = model.generate_content(prompt, generation_config=generation_config)
    
    # 3. Extrair a resposta de texto
    generated_text = response.text.strip()

    # 4. Validar a resposta gerada
    _validate_generated_response(generated_text, email_text)

    return generated_text
