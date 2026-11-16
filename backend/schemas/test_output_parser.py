import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from schemas.chat_response import ChatResponse

load_dotenv()
# Initialize Groq
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=1024,
    api_key=os.getenv("GROQ_API_KEY"),
)


# Create output parser
parser = PydanticOutputParser(
    pydantic_object=ChatResponse
)


# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful AI assistant.\n"
        "Answer the user's question.\n"
        "{format_instructions}"
    ),
    ("human", "{question}"),
])


# Insert parser instructions
prompt = prompt.partial(
    format_instructions=parser.get_format_instructions()
)


# Build chain
chain = prompt | llm | parser


# Ask a question
result = chain.invoke({
    "question": "What is the capital of Saudi Arabia?"
})


# Display structured result
print(result)

print("\nAnswer:")
print(result.answer)

print("\nLanguage:")
print(result.language)

print("\nNeeds clarification:")
print(result.needs_clarification)