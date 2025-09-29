from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import os
import shutil
from pathlib import Path

from src.rag.rag import RAG
from src.utils.config import Config


app = FastAPI(title="YARA RAG API", description="Backend API for YARA RAG assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(Config.DATA_PATH, exist_ok=True)

rag = RAG(Config.MODEL_NAME, Config.RETREIVER_NAME, Config.VECTOR_PATH, Config.DATA_PATH, Config.DEVICE)


class ChunkMetadata(BaseModel):
    score: Optional[float] = None
    source: Optional[str] = None
    page: Optional[int] = None

class Chunk(BaseModel):
    page_content: str
    metadata: ChunkMetadata

class QueryRequest(BaseModel):
    message: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    response: str
    chunks: List[Chunk]


def sanitize_metadata(metadata: Any) -> Dict[str, Any]:
    if not isinstance(metadata, dict):
        return {}

    clean_meta = {}
    for k, v in metadata.items():
        if isinstance(v, np.generic):
            v = v.item()
        if k == "page":
            if v is None:
                clean_meta[k] = None
            else:
                try:
                    clean_meta[k] = int(v)
                except (ValueError, TypeError):
                    clean_meta[k] = None
        elif k == "score":
            if v is None:
                clean_meta[k] = None
            else:
                try:
                    clean_meta[k] = float(v)
                except (ValueError, TypeError):
                    clean_meta[k] = None
        elif k == "source":
            clean_meta[k] = str(v) if v is not None else None
        else:
            if isinstance(v, (int, float, str, bool, type(None))):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)

    return clean_meta


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        raw_chunks, full_response = rag.query(request.message, request.top_k)
        chunks = []
        for chunk in raw_chunks:
            content = chunk.get("page_content", "")
            if not isinstance(content, str):
                content = str(content)

            meta = chunk.get("metadata", {})
            clean_meta = sanitize_metadata(meta)
            chunk_model = Chunk(
                page_content=content,
                metadata=ChunkMetadata(**clean_meta)
            )
            chunks.append(chunk_model)

        return QueryResponse(response=full_response, chunks=chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    saved_files = []
    try:
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"Only PDF files allowed: {file.filename}")

            file_path = os.path.join(Config.DATA_PATH, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(file.filename)

        rag.update_retriever()

        return {
            "status": "success",
            "message": f"{len(saved_files)} PDF file(s) uploaded and retriever updated.",
            "files": saved_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload or update failed: {str(e)}")

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files can be deleted")

    file_path = os.path.join(Config.DATA_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(file_path)
        rag.update_retriever()
        return {"status": "success", "message": f"File '{filename}' deleted and retriever updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.get("/documents")
async def list_documents():
    try:
        files = [f for f in os.listdir(Config.DATA_PATH) if f.endswith(".pdf")]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "OK", "model_loaded": rag is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)