from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# 1. Load the multilingual embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# 2. Connect to the multilingual Chroma collection
vector_store = Chroma(
    collection_name="company_policy_multilingual",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# 3. Define test questions
questions = [
    "How many annual leave days do employees receive?",
    "كم يومًا يحصل الموظفون على الإجازة السنوية؟"
]


# 4. Test retrieval
for question in questions:

    print("\n" + "=" * 50)
    print("Question:")
    print(question)

    results = vector_store.similarity_search(
        question,
        k=2
    )

    print("\nRetrieved Documents:")

    for document in results:
        print(document.page_content)