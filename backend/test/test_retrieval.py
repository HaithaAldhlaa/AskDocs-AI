from rag_service import retrieve_documents


# Test questions in English and Arabic
test_questions = [
    "How many annual leave days do employees receive?",
    "كم يومًا يحصل الموظفون على الإجازة السنوية؟",
    "How many unused annual leave days can employees carry forward?",
    "Does the company provide health insurance?",
]


for question in test_questions:

    print("\n" + "=" * 60)
    print("Question:", question)

    documents = retrieve_documents(question)

    print("\nFinal Retrieved Documents:", len(documents))

    for index, document in enumerate(documents, start=1):

        print(f"\nDocument {index}")
        print("Content:")
        print(document.page_content)

        print("Metadata:")
        print(document.metadata)

    print("=" * 60)