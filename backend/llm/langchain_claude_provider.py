import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage


# Initialize Claude model through LangChain
llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def generate_claude_response(messages: list) -> str:

    # Convert messages into LangChain message objects
    langchain_messages = []

    for message in messages:

        if message["role"] == "user":
            langchain_messages.append(
                HumanMessage(content=message["content"])
            )

        elif message["role"] == "assistant":
            langchain_messages.append(
                AIMessage(content=message["content"])
            )

    # Send conversation to Claude
    response = llm.invoke(langchain_messages)

    return response.content