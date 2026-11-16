# Standard Library
import hashlib
import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Third-party Libraries
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local Modules
from llm.langchain_groq_provider import (
    generate_structured_chat_response,
    generate_rag_chat_response,
    classify_query_intent,
    filter_relevant_documents,
)

from rag_service import (
    retrieve_documents,
    add_document_to_vector_store,
    delete_document_from_vector_store,
    get_document_chunks_count,
)


# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

#إنشاء مسار حفظ الملفات
#نحدد مكان documents اعتمادًا على موقع ملف main.py نفسه.
DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# لقراءة سجل المستندات.
def load_documents_registry():

    registry_path = DOCUMENTS_DIR / "documents_registry.json"

    with registry_path.open("r", encoding="utf-8") as file:
        registry = json.load(file)

    return registry

#لحفظ سجل المستندات.
def save_documents_registry(registry):

    registry_path = DOCUMENTS_DIR / "documents_registry.json"

    # 1. Create a unique temporary file
    temp_path = DOCUMENTS_DIR / f"documents_registry_{uuid4().hex}.tmp"

    try:
        # 2. Write the new data into the temporary file
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(
                registry,
                file,
                ensure_ascii=False,
                indent=4
            )

        # 3. Replace the old registry with the new file
        temp_path.replace(registry_path)

    finally:
        # 4. Remove the temporary file if it still exists
        if temp_path.exists():
            temp_path.unlink()

# لحساب بصمة الملف.هل موجود مسبقا
def calculate_file_hash(file_content: bytes) -> str:

    file_hash = hashlib.sha256(file_content).hexdigest()

    return file_hash

#دالة تستقبل بصمة ملف جديد، وتبحث عنها في سجل المستندات.
def is_duplicate_file(file_hash: str) -> bool:

    registry = load_documents_registry()

    for document in registry["documents"]:

        if document["file_hash"] == file_hash:
            return True

    return False




load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    logger.info("Groq API Key loaded successfully.")
else:
    logger.warning("Groq API Key not found.")



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"}



@app.post("/chat")
def chat(request: ChatRequest):

    conversation_id = request.conversation_id
    user_message = request.message

    try:

        # 1. Classify the question
        intent = classify_query_intent(user_message)

        sources = []

        # 2. Handle company knowledge questions
        if intent.intent == "knowledge_base":

            documents = retrieve_documents(user_message)

            if documents:

                # Filter retrieved documents for source display
                source_documents = filter_relevant_documents(
                    user_message,
                    documents
                )

                context = "\n\n".join(
                    document.page_content
                    for document in documents
                )

                ai_response = generate_rag_chat_response(
                    user_message,
                    conversation_id,
                    context
                )

                sources_by_id = {}

                for document in source_documents:

                    source_path = document.metadata.get(
                        "source",
                        "Unknown",
                    )

                    document_id = document.metadata.get("document_id")

                    if not document_id:
                        document_id = source_path

                    if document_id not in sources_by_id:
                        sources_by_id[document_id] = {
                            "document_id": document_id,
                            "filename": os.path.basename(source_path),
                            "chunks": [],
                        }

                    chunk_content = document.page_content

                    if chunk_content not in sources_by_id[document_id]["chunks"]:
                        sources_by_id[document_id]["chunks"].append(chunk_content)


                sources = list(sources_by_id.values())

            else:

                print(
                    "Knowledge Base mode: "
                    "No relevant documents found."
                )

                context = (
                    "No relevant information was found "
                    "in the uploaded documents."
                )

                ai_response = generate_rag_chat_response(
                    user_message,
                    conversation_id,
                    context
                )

        # 3. Handle general questions
        else:

            print("General chat mode.")

            ai_response = generate_structured_chat_response(
                user_message,
                conversation_id
            )

        # 4. Return response
        return {
            "reply": ai_response.answer,
            "conversation_id": conversation_id,
            "structured": {
                "answer": ai_response.answer,
                "language": ai_response.language,
                "needs_clarification": (
                    ai_response.needs_clarification
                )
            },
            "sources": sources
        }

    except Exception as e:

        print(f"Chat API Error: {e}")

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is currently unavailable. "
                "Please try again later."
            )
        )


# لرفع الملفات الى السيرفر
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    # 1. Validate file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in [".txt", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Only TXT and PDF files are allowed."
        )

    # 2. Read file content
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # 3. Calculate file hash
    file_hash = calculate_file_hash(file_content)

    # 4. Check for duplicate
    if is_duplicate_file(file_hash):
        return {
            "message": "This document already exists.",
            "original_filename": file.filename,
            "status": "duplicate"
        }

    # 5. Generate unique document ID and filename
    document_id = str(uuid4())
    unique_filename = f"{document_id}{file_extension}"

    file_path = DOCUMENTS_DIR / unique_filename

    file_saved = False

    try:
        # 1. Save original file
        with file_path.open("wb") as saved_file:
            saved_file.write(file_content)

        file_saved = True

        # 2. Process document and add chunks to ChromaDB
        chunks_count = add_document_to_vector_store(
            file_path=str(file_path),
            document_id=document_id,
            original_filename=file.filename
        )

        # 3. Create document metadata
        new_document = {
            "document_id": document_id,
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_hash": file_hash,
            "status": "processed",
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

        # 4. Save metadata in registry
        registry = load_documents_registry()
        registry["documents"].append(new_document)
        save_documents_registry(registry)

    except Exception as error:

        # 1. Rollback ChromaDB
        try:
            delete_document_from_vector_store(document_id)

        except Exception as rollback_error:
            print(f"ChromaDB rollback failed: {rollback_error}")

        # 2. Rollback original file
        if file_saved:
            try:
                if file_path.exists():
                    file_path.unlink()

            except Exception as rollback_error:
                print(f"File rollback failed: {rollback_error}")

        # 3. Return original error
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(error)}"
        )




    # 10. Return result
    return {
        "message": "File uploaded and processed successfully.",
        "document_id": document_id,
        "original_filename": file.filename,
        "status": "processed",
        "chunks_count": chunks_count
    }



# عرض الملفات المرفوعه في السيرفر
@app.get("/documents")
def list_documents():

    # 1. Load documents registry
    registry = load_documents_registry()

    # 2. Prepare document list
    documents = []

    for document in registry["documents"]:

     chunks_count = get_document_chunks_count(
        document["document_id"]
     )

     documents.append({
        "document_id": document["document_id"],
        "original_filename": document["original_filename"],
        "status": document["status"],
        "chunks_count": chunks_count,
        "uploaded_at": document.get("uploaded_at")
     })

    documents = sorted(
    documents,
    key=lambda document: document["uploaded_at"] or "",
    reverse=True )

    # 3. Return documents and total count
    return {
        "total_documents": len(documents),
        "documents": documents
    }

# حذف الملفات المرفوعه من السيرفر
@app.delete("/documents/{document_id}")
def delete_document(document_id: str):

    # 1. Load documents registry
    registry = load_documents_registry()

    # 2. Find the document
    document_to_delete = None

    for document in registry["documents"]:
        if document["document_id"] == document_id:
            document_to_delete = document
            break

    # 3. Check if document exists
    if document_to_delete is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # 4. Delete document chunks from ChromaDB
    delete_document_from_vector_store(document_id)

    # 5. Delete original file from disk
    file_path = DOCUMENTS_DIR / document_to_delete["stored_filename"]

    if file_path.exists():
        file_path.unlink()

    # 6. Remove document from registry
    registry["documents"].remove(document_to_delete)

    save_documents_registry(registry)

    # 7. Return success response
    return {
        "message": "Document deleted successfully.",
        "document_id": document_id
    }
