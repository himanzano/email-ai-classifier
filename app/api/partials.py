from fastapi import APIRouter, Request, Response
from app.config import templates

router = APIRouter(prefix="/partials", tags=["Partials"])


@router.get("/input-method/{method}", include_in_schema=False)
async def get_input_method(request: Request, method: str):
    """
    Retorna o wrapper completo (botões + área de input) para que o HTMX
    possa atualizar ambos, corrigindo o estado visual do botão selecionado.
    """
    if method in ["text", "file"]:
        return templates.TemplateResponse(
            request, "partials/input_wrapper.html", {"active_method": method}
        )
    return Response(content="Método inválido", status_code=400)


@router.get("/text-input", include_in_schema=False)
async def get_text_input_partial(request: Request):
    """
    Retorna o template parcial contendo a área de texto e o contêiner de entrada.
    """
    return templates.TemplateResponse(
        request, "partials/text_input.html", {"active_method": "text"}
    )
