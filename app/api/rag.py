from fastapi import APIRouter, UploadFile, File, status
from app.models import schemas
from app.services.rag_service import ask_question


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/ask", response_model=schemas.QueryResponse)
def ask(request: schemas.QueryRequest):
    return ask_question(request.filename, request.question)