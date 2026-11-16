from langchain_core.chat_history import InMemoryChatMessageHistory


# Store all conversations
store = {}


def get_session_history(conversation_id: str):

    if conversation_id not in store:
        store[conversation_id] = InMemoryChatMessageHistory()

    return store[conversation_id]


# Conversation 1
history_1 = get_session_history("conversation_1")

history_1.add_user_message("My name is Ahmed.")
history_1.add_ai_message("Hello Ahmed!")


# Conversation 2
history_2 = get_session_history("conversation_2")

history_2.add_user_message("My name is Mohammed.")
history_2.add_ai_message("Hello Mohammed!")


# Retrieve conversation 1
print("Conversation 1:")

for message in get_session_history("conversation_1").messages:
    print(f"{message.type}: {message.content}")


# Retrieve conversation 2
print("\nConversation 2:")

for message in get_session_history("conversation_2").messages:
    print(f"{message.type}: {message.content}")