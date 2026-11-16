from main import is_duplicate_file

# Existing file hash
existing_hash = "abc123"

# New file hash
new_hash = "xyz789"

print(
    "Existing file:",
    is_duplicate_file(existing_hash)
)

print(
    "New file:",
    is_duplicate_file(new_hash)
)