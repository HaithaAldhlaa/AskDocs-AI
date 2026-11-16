from rag_service import process_document


# Test document processing
chunks = process_document(
    file_path="documents/company_policy.txt",
    document_id="test-001",
    original_filename="company_policy.txt"
)


print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk.page_content)
    print("Metadata:", chunk.metadata)