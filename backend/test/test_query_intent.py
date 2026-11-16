from llm.langchain_groq_provider import classify_query_intent


test_questions = [
    "Does the company provide health insurance?",
    "How many annual leave days do employees receive?",
    "كم يومًا يحصل الموظفون على الإجازة السنوية؟",
    "هل توفر الشركة تأمينًا صحيًا للموظفين؟",
    "What is Python?",
    "Explain how neural networks work."
]


for question in test_questions:

    result = classify_query_intent(question)

    print("\n" + "=" * 60)
    print("Question:", question)
    print("Intent:", result.intent)
    print("Reason:", result.reason)