
from langchain_community.document_loaders import TextLoader

# Load the document
loader = TextLoader(
    "documents/company_policy.txt",
    encoding="utf-8"
)

documents = loader.load()

# Print document content
print(documents[0].page_content)

# Print document metadata
print("\nMetadata:")
print(documents[0].metadata)
