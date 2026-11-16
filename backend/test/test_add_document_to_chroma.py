from rag_service import add_document_to_vector_store


# 1. Define the test document
file_path = "documents/test_ingestion.txt"

document_id = "test-ingestion-001"

original_filename = "test_ingestion.txt"


# 2. Add the document to ChromaDB
chunks_count = add_document_to_vector_store(
    file_path=file_path,
    document_id=document_id,
    original_filename=original_filename
)


# 3. Display the result
print("Document added successfully.")
print(f"Processed chunks: {chunks_count}")