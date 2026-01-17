import json
import os
import tempfile
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, Request, UploadFile
from starlette.responses import HTMLResponse

# --- Importações de Módulos ---
from app.config import templates  # Importa da configuração central
from app.services.classifier import (
    InvalidClassificationResponseError,
    InvalidResponseJsonError,
    classify_email,
)
from app.services.responder import (
    InvalidGeneratedResponseError,
    generate_response,
)
from app.utils.preprocess import preprocess_text
from app.utils.text_extractor import extract_text


# --- Helper HTMXResponse (movido para cá) ---
class HTMXResponse(HTMLResponse):
    def __init__(
        self, request: Request, template_name: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        toast_details = {
            key.replace("toast_", ""): value
            for key, value in kwargs.items()
            if key.startswith("toast_")
        }
        kwargs = {key: value for key, value in kwargs.items() if not key.startswith("toast_")}

        if context is None: context = {}
        context.setdefault("request", request)
        content = templates.get_template(template_name).render(context)

        headers = kwargs.setdefault("headers", {})
        if toast_details.get("type") and toast_details.get("title"):
            headers["HX-Trigger"] = json.dumps({"toast": toast_details})

        super().__init__(content=content, **kwargs)


# --- Definição do Router ---
router = APIRouter(tags=["Email Processing"])


# --- Implementação do Endpoint ---
@router.post("/api/process-email")
async def process_email_endpoint(
    request: Request,
    email_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if (email_content is None and file is None) or (email_content is not None and file is not None):
        return HTMXResponse(
            request, "partials/error_display.html",
            context={"error_message": "Forneça texto ou um arquivo, não ambos."},
            status_code=400,
            toast_type="error", toast_title="Erro de Validação",
            toast_description="É necessário enviar apenas uma fonte de conteúdo.",
        )

    raw_content, temp_file_path = "", None
    try:
        if file and file.filename:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(await file.read())
                temp_file_path = temp_file.name
            raw_content = extract_text(temp_file_path)
        elif email_content:
            raw_content = extract_text(email_content)

        if not raw_content.strip():
            return HTMXResponse(
                request, "partials/error_display.html",
                context={"error_message": "O conteúdo do e-mail está vazio."},
                status_code=400,
                toast_type="error", toast_title="Erro de Conteúdo",
                toast_description="O e-mail parece estar vazio ou não pôde ser lido.",
            )

        processed_text = preprocess_text(raw_content, remove_stopwords=True, lemmatize=True)
        classification_result = classify_email(processed_text)
        category = classification_result["category"]
        suggested_response = generate_response(raw_content, category)

        return HTMXResponse(
            request, "partials/result_display.html",
            context={
                "category": category,
                "confidence": classification_result["confidence"],
                "reason": classification_result["reason"],
                "response": suggested_response,
            },
            toast_type="success", toast_title="E-mail Analisado",
            toast_description=f"Classificado como '{category}'.",
        )

    except (InvalidClassificationResponseError, InvalidResponseJsonError, InvalidGeneratedResponseError) as e:
        return HTMXResponse(
            request, "partials/error_display.html",
            context={"error_message": f"Erro ao processar a resposta da IA: {e}"},
            status_code=500,
            toast_type="error", toast_title="Erro na IA",
            toast_description="A resposta do modelo de IA foi inválida.",
        )
    except Exception as e:
        return HTMXResponse(
            request, "partials/error_display.html",
            context={"error_message": f"Ocorreu um erro inesperado: {e}"},
            status_code=500,
            toast_type="error", toast_title="Erro Inesperado",
            toast_description="Não foi possível processar a solicitação.",
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)