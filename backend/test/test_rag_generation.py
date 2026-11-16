
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from schemas.rag_response import RAGResponse, Source


# 1. Load environment variables
load_dotenv()


# 2. Initialize the LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


# 3. Initialize the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 4. Connect to the existing Chroma database
vector_store = Chroma(
    collection_name="company_policy",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# 5. Define the user's question
question = "How many annual leave days do employees receive?"


# 6. Retrieve relevant documents
retrieved_results = vector_store.similarity_search_with_relevance_scores(
    question,
    k=2
)

# Define the minimum relevance score
threshold = 0.50

# Keep only relevant documents
retrieved_docs = [
    document
    for document, score in retrieved_results
    if score >= threshold
]

# Check whether relevant documents were found
if not retrieved_docs:
    print("No relevant information found in the documents.")
    exit()



# 7. Convert retrieved documents into context
context = "\n\n".join(
    document.page_content
    for document in retrieved_docs
)


# 8. Create the RAG prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an assistant that answers questions using
        the provided context.

        Rules:
        - Answer using only the information in the context.
        - Do not invent or assume information.
        - If the context does not contain the answer,
          clearly say that the information is not available.
        - Give a clear and concise answer."""
    ),
    (
        "human",
        """Context:
        {context}

        Question:
        {question}"""
    )
])


# 9. Build the RAG chain
rag_chain = prompt | llm


# 10. Generate the answer
response = rag_chain.invoke({
    "context": context,
    "question": question
})


# Extract unique sources
sources = list(set(
    document.metadata.get("source", "Unknown")
    for document in retrieved_docs
))

# Create structured source objects
source_objects = [
    Source(
        filename=source.split("/")[-1],
        path=source
    )
    for source in sources
]

# Create structured RAG response
rag_response = RAGResponse(
    answer=response.content,
    sources=source_objects
)

# Display structured response
print("\n--- Structured RAG Response ---")
print(rag_response.model_dump_json(indent=2))