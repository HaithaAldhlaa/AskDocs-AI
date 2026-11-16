
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. Load the document
loader = TextLoader(
    "documents/company_policy.txt",
    encoding="utf-8"
)

documents = loader.load()


# 2. Create the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)


# 3. Split the document
chunks = text_splitter.split_documents(documents)


# 4. Print the results
print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks):

    print(f"\n--- Chunk {index + 1} ---")

    print(chunk.page_content)

    print("\nMetadata:")
    print(chunk.metadata)
