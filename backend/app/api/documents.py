from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas import DocumentInfo, DocumentList
from app.services import ingest, vector_store

router = APIRouter(tags=["documents"])

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


@router.get("/documents", response_model=DocumentList)
async def list_documents() -> DocumentList:
    docs = [DocumentInfo(source=str(d["source"]), chunks=int(d["chunks"])) for d in vector_store.list_sources()]
    return DocumentList(documents=docs, total_chunks=sum(d.chunks for d in docs))


@router.post("/documents", response_model=DocumentInfo, status_code=201)
async def upload_document(file: UploadFile) -> DocumentInfo:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 20 MB.")

    try:
        result = ingest.ingest_bytes(data, file.filename or "upload")
    except ingest.UnsupportedFileError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return DocumentInfo(source=result.source, chunks=result.chunks)


@router.delete("/documents/{source}", status_code=204)
async def delete_document(source: str) -> None:
    if vector_store.delete_source(source) == 0:
        raise HTTPException(status_code=404, detail=f"No document named '{source}'.")
