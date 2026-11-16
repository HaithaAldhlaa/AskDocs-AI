from schemas.chat_response import ChatResponse


response = ChatResponse(
    answer="Riyadh is the capital of Saudi Arabia.",
    language="English",
    needs_clarification=False
)


print(response)

print("\nAnswer:")
print(response.answer)

print("\nLanguage:")
print(response.language)

print("\nNeeds clarification:")
print(response.needs_clarification)