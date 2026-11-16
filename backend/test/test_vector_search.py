
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 1. Load the document
loader = TextLoader(
    "documents/company_policy.txt",
    encoding="utf-8"
)

documents = loader.load()


# 2. Split the document into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = text_splitter.split_documents(documents)


# 3. Load the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 4. Create the vector database
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="company_policy",
    persist_directory="./chroma_db"
)


# 5. Search for relevant information
question = "How many vacation days do employees receive?"
results = vector_store.similarity_search(
    question,
    k=2
)


# 6. Print the results
for index, result in enumerate(results):
    print(f"\n--- Result {index + 1} ---")
    print(result.page_content)
    print("Metadata:")
    print(result.metadata)
