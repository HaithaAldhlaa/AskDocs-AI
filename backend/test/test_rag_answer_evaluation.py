
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="company_policy",
    persist_directory="./chroma_db",
    embedding_function=embeddings,
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    max_tokens=1024,
)



test_cases = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected_keywords": ["21 days"],
    },
    {
        "question": "How many unused annual leave days can employees carry forward?",
        "expected_keywords": ["5", "unused annual leave days"],
    },
    {
        "question": "Does the company provide health insurance?",
        "expected_keywords": ["Not available in the documents"],
    },
]




prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a company policy assistant.

        Answer using only the provided context.

        Do not invent information.

        If the answer is not available in the context,
        say:
        Not available in the documents.

        Answer in English.
        """
    ),
    (
        "human",
        """
        Context:
        {context}

        Question:
        {question}
        """
    ),
])


rag_chain = prompt | llm


distance_threshold = 1.0

for test_case in test_cases:

    question = test_case["question"]
    expected_answer = test_case["expected_keywords"]

    print("\n" + "=" * 50)
    print("Question:")
    print(question)

    # Retrieve documents
    results = vector_store.similarity_search_with_score(
        question,
        k=2
    )

    # Filter documents by distance
    retrieved_docs = [
        document
        for document, distance in results
        if distance <= distance_threshold
    ]

    # Generate answer
    if retrieved_docs:

        context = "\n\n".join(
            document.page_content
            for document in retrieved_docs
        )

        response = rag_chain.invoke({
            "context": context,
            "question": question
        })

        actual_answer = response.content

    else:

        actual_answer = "Not available in the documents"

    # Evaluate answer

    # Evaluate answer
    expected_keywords = test_case["expected_keywords"]

    evaluation = all(
        keyword.lower() in actual_answer.lower()
        for keyword in expected_keywords
    )

    print("\nExpected Keywords:")
    print(expected_keywords)

    print("\nActual Answer:")
    print(actual_answer)

    print("\nEvaluation:")
    print("PASS" if evaluation else "FAIL")
