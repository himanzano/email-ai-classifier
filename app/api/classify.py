import os
import tempfile
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel

# --- Importação dos Módulos de Lógica ---
from app.utils.text_extractor import extract_text
from app.utils.preprocess import preprocess_text
from app.services.classifier import classify_email, InvalidClassificationResponseError, InvalidResponseJsonError
from app.services.responder import generate_response, InvalidGeneratedResponseError

# --- Definição do Router ---
router = APIRouter(
    tags=["Email Processing"],
)

# --- Modelos de Dados (Pydantic) ---

class ClassificationResponse(BaseModel):
    """Modelo de saída para a resposta da API."""
    category: str
    confidence: float
    reason: str
    response: str

# --- Implementação do Endpoint ---

@router.post("/api/process-email", response_model=ClassificationResponse)
async def process_email_endpoint(
    email_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Recebe o conteúdo de um e-mail (via texto ou arquivo), processa-o através
    do pipeline completo e retorna a classificação e uma resposta sugerida.
    """
    if (email_content is None and file is None) or (email_content is not None and file is not None):
        raise HTTPException(
            status_code=400,
            detail="Forneça exatamente uma fonte de conteúdo: o campo de formulário 'email_content' ou um arquivo, não ambos ou nenhum."
        )

    raw_content = ""
    temp_file_path = None

    try:
        if file is not None:
            if not file.filename:
                raise HTTPException(status_code=400, detail="O arquivo enviado não possui um nome de arquivo.")
            
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(await file.read())
                temp_file_path = temp_file.name
            raw_content = extract_text(temp_file_path)
        
        elif email_content is not None:
            raw_content = extract_text(email_content)

        if not raw_content.strip():
            raise HTTPException(status_code=400, detail="O conteúdo do e-mail está vazio ou não pôde ser lido.")

        processed_text = preprocess_text(
            raw_content,
            remove_stopwords=True,
            lemmatize=True,
            normalize_numbers=True
        )

        classification_result = classify_email(processed_text)
        category = classification_result["category"]

        suggested_response = generate_response(raw_content, category)
        
        return {
            "category": category,
            "confidence": classification_result["confidence"],
            "reason": classification_result["reason"],
            "response": suggested_response
        }

    except (InvalidClassificationResponseError, InvalidResponseJsonError, InvalidGeneratedResponseError) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a resposta da IA: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno inesperado: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)