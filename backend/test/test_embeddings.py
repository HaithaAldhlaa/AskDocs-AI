from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Load document
loader = TextLoader(
    "documents/company_policy.txt",
    encoding="utf-8"
)

documents = loader.load()

# 2. Split document into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = text_splitter.split_documents(documents)

# 3. Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 4. Convert chunks into embeddings
vectors = embeddings.embed_documents(

    [chunk.page_content for chunk in chunks]
)

# 5. Display results
print(f"Total chunks: {len(chunks)}")
print(f"Total embeddings: {len(vectors)}")

for index, vector in enumerate(vectors):
    print(f"\n--- Embedding {index + 1} ---")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
