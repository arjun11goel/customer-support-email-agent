from fastapi import APIRouter, Depends, HTTPException

from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()


@router.get("/knowledge-base")
def list_knowledge_documents():
    """List Markdown files available for retrieval."""
    service = KnowledgeBaseService()
    return {"documents": service.list_documents()}


@router.get("/knowledge-base/{filename}")
def get_knowledge_document(filename: str):
    """Read one Markdown document."""
    service = KnowledgeBaseService()

    try:
        content = service.read_document(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "filename": filename,
        "content": content,
    }


@router.post("/knowledge-base/rebuild")
def rebuild_knowledge_index():
    """Rebuild the FAISS index from the knowledge Markdown files."""
    try:
        return KnowledgeBaseService().rebuild_index()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc