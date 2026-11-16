from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from pdf2text_arabic import extract_pdf_result

from pathlib import Path

from langchain_community.document_loaders import (TextLoader,PyPDFLoader)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document




# 1. Initialize multilingual embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# 2. Connect to the multilingual Chroma collection
vector_store = Chroma(
    collection_name="company_policy_multilingual",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# 3. Define the distance threshold
DISTANCE_THRESHOLD = 21


def process_document(
    file_path: str,
    document_id: str,
    original_filename: str
):
    print("DEBUG: process_document started!", flush=True)
    # 1. Get the file extension
    # 1. Get the file extension
    file_extension = Path(file_path).suffix.lower()

    # 2. Load the document
    if file_extension == ".txt":

        loader = TextLoader(
            file_path,
            encoding="utf-8"
        )

        documents = loader.load()


    elif file_extension == ".pdf":

        print("\n========== PDF2Text-Arabic Extraction ==========")

        # Extract PDF text locally without cloud OCR
        result = extract_pdf_result(
            file_path,
            ocr_strategy="never"
        )

        extracted_text = result.text.strip()

        print("Total pages:", result.pages_total)
        print("Pages with text:", result.pages_with_text)
        print("Empty pages:", result.empty_pages)
        print("Mixed pages:", result.mixed_pages)
        print("Total characters:", len(extracted_text))

        if extracted_text:

            print("\n========== Extracted Text ==========")
            print(extracted_text, flush=True)

            documents = [
                Document(
                    page_content=extracted_text,
                    metadata={
                        "page_count": result.pages_total,
                        "extractor": "pdf2text-arabic"
                    }
                )
            ]

        else:
            documents = []


    else:
        raise ValueError("Unsupported file format.")




    # 3. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    """print("\n========== Generated Chunks ==========", flush=True)
    print("Total chunks:", len(chunks), flush=True)

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {i} ---")
        print(chunk.page_content, flush=True)

    print("\n========== CHUNKS DEBUG ==========", flush=True)

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {i} ---", flush=True)
        print(chunk.page_content, flush=True)

    print("==================================\n", flush=True)"""

    # 4. Add metadata to each chunk
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        chunk.metadata["source"] = original_filename

    # 5. Return processed chunks
    return chunks

def add_document_to_vector_store(
    file_path: str,
    document_id: str,
    original_filename: str
):
    # 1. Process the document
    chunks = process_document(
        file_path=file_path,
        document_id=document_id,
        original_filename=original_filename
    )

    # 2. Check if the document contains chunks
    if not chunks:
        raise ValueError("No text content found in the document.")

    # 3. Add chunks to ChromaDB
    vector_store.add_documents(chunks)

    # 4. Return the number of added chunks
    return len(chunks)

# delete document from vector_store
def delete_document_from_vector_store(document_id: str):

    vector_store.delete(
        where={"document_id": document_id}
    )

#داله لارجاع عدد المقاطع في الملف الواحد
def get_document_chunks_count(document_id: str):

    results = vector_store.get(
        where={"document_id": document_id}
    )

    return len(results["ids"])

 # 4. Retrieve relevant documents
"""def retrieve_documents(question: str):

    results = vector_store.similarity_search_with_score(
        question,
        k=2
    )

    relevant_documents = [
        document
        for document, distance in results
        if distance <= DISTANCE_THRESHOLD
    ]

    return relevant_documents """



def retrieve_documents(question: str):

    results = vector_store.similarity_search_with_score(
        question,
        k=5
    )

    """print("\n========== Retrieval Results ==========")

    for index, (document, distance) in enumerate(results, start=1):

        print(f"\nResult {index}")
        print(f"Distance: {distance}")
        print(f"Content: {document.page_content}")"""

    relevant_documents = [
        document
        for document, distance in results
        if distance <= DISTANCE_THRESHOLD
    ]

    print("\nRelevant Documents:", len(relevant_documents))
    print("=======================================\n")

    return relevant_documents
