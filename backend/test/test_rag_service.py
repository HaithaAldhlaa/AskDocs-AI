from rag_service import retrieve_documents


questions = [
    "How many annual leave days do employees receive?",
    "كم يومًا يحصل الموظفون على الإجازة السنوية؟",
    "Does the company provide health insurance?",
]


for question in questions:

    print("\n" + "=" * 50)
    print("Question:")
    print(question)

    documents = retrieve_documents(question)

    print("\nRetrieved Documents:")
    print(len(documents))

    for document in documents:
        print(document.page_content)