from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# 1. Load the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 2. Connect to the existing Chroma database
vector_store = Chroma(
    collection_name="company_policy",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


# 3. Define evaluation questions
test_cases = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected_keyword": "21 days",
        "expected_relevant": True
    },
    {
        "question": "How many unused annual leave days can employees carry forward?",
        "expected_keyword": "5 unused annual leave days",
        "expected_relevant": True
    },
    {
        "question": "Does the company provide health insurance?",
        "expected_keyword": None,
        "expected_relevant": False
    }
]


# 4. Define the relevance threshold
threshold = 0.50


# 5. Run evaluation
for test_case in test_cases:

    question = test_case["question"]

    # Retrieve documents
    results = vector_store.similarity_search_with_score(
        question,
        k=2
    )

    # Filter by distance
    distance_threshold = 1.0

    retrieved_docs = [
        document
        for document, distance in results
        if distance <= distance_threshold
    ]

    # Check expected information
    if test_case["expected_relevant"]:

        expected_keyword = test_case["expected_keyword"]

        relevant_found = any(
            expected_keyword.lower() in document.page_content.lower()
            for document in retrieved_docs
        )

        recall_at_k = 1.0 if relevant_found else 0.0

    else:

        relevant_found = not retrieved_docs

        recall_at_k = None

    # Print evaluation for each question
    print("\n" + "=" * 50)

    print("Question:")
    print(question)

    print("\nRetrieved Documents:")
    print(len(retrieved_docs))

    print("\nExpected Information Found:")
    print(relevant_found)

    if recall_at_k is not None:
        print("\nRecall@K:")
        print(recall_at_k)

    print("\nEvaluation:")
    print("PASS" if relevant_found else "FAIL")