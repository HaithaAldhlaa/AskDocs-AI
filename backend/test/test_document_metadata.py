from rag_service import retrieve_documents

documents = retrieve_documents(
    "How many annual leave days do employees receive?"
)

for document in documents:
    print("Content:")
    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)

    print("=" * 50)