import json
from pathlib import Path

from rag_service import process_document, vector_store


# 1. Load the documents registry
documents_dir = Path(__file__).resolve().parent / "documents"
registry_path = documents_dir / "documents_registry.json"

with registry_path.open("r", encoding="utf-8") as file:
    registry = json.load(file)


# 2. Get the uploaded document
document = registry["documents"][0]

document_id = document["document_id"]
stored_filename = document["stored_filename"]
original_filename = document["original_filename"]

file_path = documents_dir / stored_filename


# 3. Check whether this document already exists in ChromaDB
existing = vector_store.get(
    where={"document_id": document_id}
)

if existing["ids"]:
    print("Document already exists in ChromaDB.")
    print("Existing chunks:", len(existing["ids"]))

else:
    # 4. Process and add the document
    chunks = process_document(
        file_path=str(file_path),
        document_id=document_id,
        original_filename=original_filename
    )

    # 5. Verify insertion
    result = vector_store.get(
        where={"document_id": document_id}
    )

    print("Document added successfully.")
    print("Processed chunks:", len(chunks))
    print("Stored chunks:", len(result["ids"]))

    # 6. Update document status
    document["status"] = "processed"

    with registry_path.open("w", encoding="utf-8") as file:
        json.dump(registry, file, ensure_ascii=False, indent=4)