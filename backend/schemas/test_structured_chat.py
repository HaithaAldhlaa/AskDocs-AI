from llm.langchain_groq_provider import generate_structured_chat_response


# Test 1: Clear question
response1 = generate_structured_chat_response(
    "What is the capital of Saudi Arabia?",
    "clarification_test_1"
)

print("\nTest 1: Clear question")
print(response1.model_dump())


# Test 2: Missing essential information
response2 = generate_structured_chat_response(
    "Help me choose the best option.",
    "clarification_test_2"
)

print("\nTest 2: Missing information")
print(response2.model_dump())


# Test 3: Use conversation history
conversation_id = "clarification_test_3"

generate_structured_chat_response(
    "I am learning Python.",
    conversation_id
)

response3 = generate_structured_chat_response(
    "What programming language am I learning?",
    conversation_id
)

print("\nTest 3: Conversation history")
print(response3.model_dump())
