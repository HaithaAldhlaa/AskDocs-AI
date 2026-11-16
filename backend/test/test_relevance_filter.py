from rag_service import retrieve_documents
from llm.langchain_groq_provider import filter_relevant_documents


test_questions = [
    "How many annual leave days do employees receive?",
    "كم يومًا يحصل الموظفون على الإجازة السنوية؟",
    "How many unused annual leave days can employees carry forward?",
    "Does the company provide health insurance?",
]


for question in test_questions:

    print("\n" + "=" * 60)
    print(f"Question: {question}")

    # Step 1: Retrieve documents using vector similarity
    retrieved_documents = retrieve_documents(question)

    print(f"\nRetrieved chunks: {len(retrieved_documents)}")

    # Step 2: Filter retrieved documents using the LLM
    relevant_documents = filter_relevant_documents(
        question,
        retrieved_documents
    )

    print(f"\nRelevant chunks: {len(relevant_documents)}")

    # Step 3: Display the filtered results
    for index, document in enumerate(relevant_documents, start=1):
        print(f"\nChunk {index}:")
        print(document.page_content)