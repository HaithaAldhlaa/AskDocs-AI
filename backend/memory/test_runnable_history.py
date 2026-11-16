from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv


load_dotenv()


# Store conversations
store = {}


def get_session_history(conversation_id: str):

    if conversation_id not in store:
        store[conversation_id] = InMemoryChatMessageHistory()

    return store[conversation_id]


# Initialize Groq
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=1024,
)


# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


# Build the chain
chain = prompt | llm


# Attach conversation history
chat_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


# First message
response1 = chat_with_history.invoke(
    {"input": "My name is Ahmed."},
    config={"configurable": {"session_id": "conversation_1"}},
)

print("AI:", response1.content)


# Second message
response2 = chat_with_history.invoke(
    {"input": "What is my name?"},
    config={"configurable": {"session_id": "conversation_1"}},
)

print("AI:", response2.content)


# Display stored messages
print("\nConversation History:")

for message in get_session_history("conversation_1").messages:
    print(f"{message.type}: {message.content}")