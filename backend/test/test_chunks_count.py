from rag_service import get_document_chunks_count

document_id = "09cd969e-78dc-46c4-b9de-f05713662618"

chunks_count = get_document_chunks_count(document_id)

print("Document chunks count:", chunks_count)