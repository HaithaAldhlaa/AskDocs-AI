import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


from langchain_core.output_parsers import PydanticOutputParser
from schemas.chat_response import ChatResponse
from schemas.relevant_documents import RelevantDocuments

from schemas.query_intent import QueryIntent


load_dotenv()

# Store conversation histories
store = {}


def get_session_history(conversation_id: str):

    if conversation_id not in store:
        store[conversation_id] = InMemoryChatMessageHistory()

    return store[conversation_id]


# Initialize Groq model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("GROQ_API_KEY"),
)


# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are {assistant_role}. "
        "Answer the user in {language}. "
        "Do not use any other language. "
        "Be clear and helpful."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


# Create LangChain chain
chain = prompt | llm


# Attach conversation history
chat_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


def generate_response(user_message: str, conversation_id: str) -> str:

    response = chat_with_history.invoke(
        {
            "input": user_message,
            "assistant_role": "AI assistant",
            "language": "English",
        },
        config={
            "configurable": {
                "session_id": conversation_id
            }
        },
    )

    return response.content



def generate_structured_chat_response(user_message: str,conversation_id: str) -> ChatResponse:

    # 1. Create output parser
    parser = PydanticOutputParser(pydantic_object=ChatResponse)

    # 2. Create structured prompt
    structured_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
    "You are a helpful AI assistant.\n"
    "Understand questions in any language."
    "You MUST answer in English or arabic depend on question.\n"
    "Use the conversation history when answering.\n"
    "\n"
    "Clarification rules:\n"
    "1. Set needs_clarification to true when essential "
    "information is missing and you cannot provide a useful "
    "answer without it.\n"
    "2. When clarification is needed, ask a specific and "
    "relevant question in the answer field.\n"
    "3. Set needs_clarification to false when you can "
    "provide a useful answer based on the available information.\n"
    "4. Do not ask unnecessary questions.\n"
    "5. Do not ask again for information already provided "
    "in the conversation history.\n"
    "\n"
    "Return your response using the required format.\n"
    "{format_instructions}"


        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    # 3. Add format instructions
    structured_prompt = structured_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    # 4. Create chain WITHOUT the output parser
    structured_chain = structured_prompt | llm

    # 5. Attach conversation history
    structured_chat = RunnableWithMessageHistory(
        structured_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # 6. Invoke the chain
    response = structured_chat.invoke(
        {"input": user_message},
        config={
            "configurable": {
                "session_id": conversation_id
            }
        },
    )

    # 7. Parse the response AFTER history handling
    structured_response = parser.parse(response.content)

    return structured_response

# RAG Chat_Response Generation Function
def generate_rag_chat_response(
    user_message: str,
    conversation_id: str,
    context: str  # context is the text extaction from ChromaDB vectorDB.
) -> ChatResponse:

    # 1. Create output parser
    parser = PydanticOutputParser(pydantic_object=ChatResponse)

    # 2. Create RAG prompt
    rag_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a helpful AI assistant.

You MUST answer in English or arabic depend on question.

Use the conversation history to understand the user's question.

Use the following retrieved documents as the source
of factual information:

{context}

Rules:
1. Understand questions in any language.
2. Answer factual questions using only the retrieved documents.
3. Do not invent information that is not present in the documents.
4. If the documents do not contain the requested information,
   clearly say that the information is not available
   in the uploaded documents.
5. Use conversation history to understand references
   and follow-up questions.
6. Do not ask unnecessary clarification questions.

Return your response using the required format.

{format_instructions}
            """
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    # 3. Add format instructions
    rag_prompt = rag_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    # 4. Create chain
    rag_chain = rag_prompt | llm

    # 5. Attach conversation history
    rag_chat = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # 6. Invoke the chain
    response = rag_chat.invoke(
        {
            "input": user_message,
            "context": context,
        },
        config={
            "configurable": {
                "session_id": conversation_id
            }
        },
    )

    # 7. Parse structured response
    structured_response = parser.parse(response.content)

    return structured_response

# داله لتصنيف نوع السؤال هل عام او يختص بملفات ال RAG
def classify_query_intent(user_message: str) -> QueryIntent:

    parser = PydanticOutputParser(
        pydantic_object=QueryIntent
    )

    classifier_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a query intent classifier.

Your task is to classify the user's question into one of two categories:

1. knowledge_base:
   Questions about company policies, employee benefits,
   annual leave, HR rules, internal procedures,
   company documents, and organizational information.

2. general:
   General knowledge questions, programming,
   technology, education, science, and other topics
   unrelated to company documents.

Important rules:
- Understand questions in Arabic and English.
- Classify based on the meaning, not just keywords.
- A question about company information remains knowledge_base
  even if the required information may be missing.
- Do not answer the user's question.
- Return only the required structured result.

{format_instructions}
            """
        ),
        ("human", "{input}"),
    ])

    classifier_prompt = classifier_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    classifier_chain = classifier_prompt | llm

    response = classifier_chain.invoke({
        "input": user_message
    })

    return parser.parse(response.content)

# داله لارجاع أرقام المقاطع ذات الصلة في قائمة منظمة، بدلاً من إرجاع إجابة نصية يصعب التعامل معها برمجياً.
def filter_relevant_documents(question: str, documents: list) -> list:
    # 1. Return an empty list if there are no documents
    if not documents:
        return []

    # 2. Create an output parser
    parser = PydanticOutputParser(
        pydantic_object=RelevantDocuments
    )

    # 3. Create the filtering prompt
    filter_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a document relevance evaluator.

            Your task is to identify which retrieved document chunks
            directly support answering the user's question.

            Rules:
            - Understand questions in any language.
            - Select chunks that provide useful evidence for answering
              the question.
            - Do not select chunks only because they discuss the same topic.
            - Do not invent information.
            - Return an empty list if no chunk is relevant.
            - Return only zero-based chunk indices.

            {format_instructions}
            """
        ),
        (
            "human",
            """
            Question:
            {question}

            Retrieved document chunks:
            {chunks}
            """
        )
    ])

    # 4. Add the parser instructions to the prompt
    filter_prompt = filter_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    # 5. Connect the prompt to the LLM
    filter_chain = filter_prompt | llm

    # 6. Prepare the documents with their indices
    formatted_chunks = "\n\n".join(
        f"Chunk {index}:\n{document.page_content}"
        for index, document in enumerate(documents)
    )

    # 7. Ask the LLM to identify relevant chunks
    response = filter_chain.invoke({
        "question": question,
        "chunks": formatted_chunks
    })

    # 8. Convert the LLM response into our Pydantic model
    result = parser.parse(response.content)

    # 9. Keep only valid indices
    valid_indices = {
        index
        for index in result.relevant_indices
        if 0 <= index < len(documents)
    }

    # 10. Return the relevant documents
    return [
        document
        for index, document in enumerate(documents)
        if index in valid_indices
    ]