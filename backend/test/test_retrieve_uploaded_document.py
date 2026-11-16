from rag_service import retrieve_documents


# 1. Define a question about the test document
question = "Does the company provide health insurance?"


# 2. Retrieve relevant documents
documents = retrieve_documents(question)


# 3. Display the results
print(f"Retrieved documents: {len(documents)}")

for index, document in enumerate(documents, start=1):
    print(f"\n--- Retrieved Document {index} ---")
    print(document.page_content)
    print("Metadata:", document.metadata)