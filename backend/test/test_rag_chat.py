from llm.langchain_groq_provider import generate_rag_chat_response


# Retrieved documents (Context)
context = """
Company Policy

Employees receive 21 days of annual leave.

Annual leave requests must be submitted
at least 5 days before the requested date.

Employees can carry forward a maximum
of 5 unused annual leave days.
"""


# Use the same conversation ID for both questions
conversation_id = "rag-integration-test-001"


# Test 1: Ask the first question
question_1 = "How many annual leave days do employees receive?"

response_1 = generate_rag_chat_response(
    question_1,
    conversation_id,
    context
)

print("\n--- Test 1 ---")
print(response_1.model_dump_json(indent=2))


# Test 2: Ask a follow-up question
question_2 = "And how many unused days can they carry forward?"

response_2 = generate_rag_chat_response(
    question_2,
    conversation_id,
    context
)

print("\n--- Test 2 ---")
print(response_2.model_dump_json(indent=2))