from llm.langchain_groq_provider import generate_structured_response


response = generate_structured_response(
    "What is the capital of Saudi Arabia?"
)


print("Answer:", response.answer)

print("Language:", response.language)

print("Needs clarification:", response.needs_clarification)