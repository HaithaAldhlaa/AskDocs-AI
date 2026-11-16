# Store conversations in memory
conversations = {}


def get_conversation(conversation_id: str, limit: int = 20) -> list:
    messages = conversations.get(conversation_id, [])
    return messages[-limit:]


def add_message(conversation_id: str, role: str, content: str):
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversations[conversation_id].append({
        "role": role,
        "content": content
    })