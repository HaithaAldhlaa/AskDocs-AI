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


# 2. Split the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = text_splitter.split_documents(documents)


# 3. Initialize multilingual embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# 4. Create a new multilingual Chroma collection
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="company_policy_multilingual",
    persist_directory="./chroma_db"
)


print("Multilingual ChromaDB created successfully!")
print(f"Number of chunks: {len(chunks)}")