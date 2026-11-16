from main import calculate_file_hash


file_content_1 = b"Employees receive 21 days of annual leave."

file_content_2 = b"Employees receive 21 days of annual leave."

file_content_3 = b"Employees receive 30 days of annual leave."


hash_1 = calculate_file_hash(file_content_1)
hash_2 = calculate_file_hash(file_content_2)
hash_3 = calculate_file_hash(file_content_3)


print("Hash 1:", hash_1)
print("Hash 2:", hash_2)
print("Hash 3:", hash_3)

print("Same content:", hash_1 == hash_2)
print("Different content:", hash_1 != hash_3)