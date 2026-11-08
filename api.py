from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline

from config import LLM_MODEL_NAME, PDF_DIR
from ingestion import create_or_update_vectorstore
from retrieval import retrieve_documents
from app import generate_answer, REFUSAL


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\nInitializing RAG API...", flush=True)

    # Initialize PDF ingestion and Chroma vector database
    app.state.vectorstore = create_or_update_vectorstore()

    print("\nRAG vector database initialized.", flush=True)

    # Load Qwen language model
    print("\nLoading Qwen model...", flush=True)

    app.state.generator = pipeline(
        "text-generation",
        model=LLM_MODEL_NAME
    )

    print("\nQwen model loaded successfully.", flush=True)
    print("\nRAG API is ready!", flush=True)

    yield


app = FastAPI(
    title="Local PDF RAG API",
    description="Backend API for the Local PDF RAG Assistant",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():

    return {
        "message": "Local PDF RAG API is running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "Local PDF RAG API"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a valid question.",
            "sources": []
        }

    # Retrieve relevant documents
    retrieved = retrieve_documents(
        app.state.vectorstore,
        question
    )

    if retrieved is None:
        return {
            "question": question,
            "answer": REFUSAL,
            "sources": []
        }

    context, results = retrieved

    # Generate answer using Qwen
    answer = generate_answer(
        app.state.generator,
        question,
        context
    )

    # Prepare source information
    sources = []

    for doc in results:

        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")

        source_info = {
            "file": source,
            "page": page + 1 if page is not None else None
        }

        if source_info not in sources:
            sources.append(source_info)

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }

@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):

    data_dir = PDF_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    try:
        for uploaded_file in files:

            filename = Path(uploaded_file.filename).name

            if not filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF files are allowed: {filename}"
                )

            file_content = await uploaded_file.read()

            max_file_size = 1024 * 1024 * 1024  # 1 GB

            if len(file_content) > max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum allowed size is 1 GB: {filename}"
                )

            if not file_content:
                raise HTTPException(
                    status_code=400,
                    detail=f"Empty PDF file: {filename}"
                )

            file_path = data_dir / filename
            file_path.write_bytes(file_content)

            uploaded_files.append(filename)

        updated_vectorstore = create_or_update_vectorstore()

        if updated_vectorstore is None:
            raise RuntimeError("Vector database update failed.")

        app.state.vectorstore = updated_vectorstore

        return {
            "status": "success",
            "message": "PDFs uploaded and indexed successfully.",
            "uploaded_files": uploaded_files
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF upload failed: {str(error)}"
        )

@app.get("/pdf/{filename}")
def open_pdf(filename: str):

    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    pdf_path = PDF_DIR / filename

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        content_disposition_type="inline"
    )   

@app.get("/pdf/{filename}")
def open_pdf(filename: str):

    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    pdf_path = PDF_DIR / filename

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        content_disposition_type="inline"
    )


@app.delete("/pdf/{filename}")
def delete_pdf(filename: str):

    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    pdf_path = PDF_DIR / filename

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    try:
        records = app.state.vectorstore.get(
            where={"source": str(pdf_path)},
            include=["metadatas"]
        )

        ids = records.get("ids", [])

        if ids:
            app.state.vectorstore.delete(ids=ids)

        pdf_path.unlink()

        return {
            "status": "success",
            "message": f"{filename} deleted successfully.",
            "deleted_chunks": len(ids)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF deletion failed: {str(error)}"
        )