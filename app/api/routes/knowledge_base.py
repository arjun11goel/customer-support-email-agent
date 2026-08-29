from fastapi import APIRouter

from app.services.knowledge_base_service import (
    KnowledgeBaseService,
)

router = APIRouter()


@router.get("/knowledge-base")
def list_knowledge_documents():
    service = KnowledgeBaseService()

    return {
        "documents": service.list_documents(),
    }


@router.get("/knowledge-base/{filename}")
def get_knowledge_document(filename: str):
    service = KnowledgeBaseService()

    return {
        "filename": filename,
        "content": service.read_document(filename),
    }