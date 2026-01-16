"""Utility script to rename image files in a structured manner."""

import os

path_list = [
    ".//static//1M00-20240206154354",
    ".//static//2K18-20240206162448",
    ".//static//9N57-20240206164929",
    ".//static//1M00_2-20240206154354",
    ".//static//2K18_2-20240206162448",
    ".//static//9N57_2-20240206164929",
]

for j in range(len(path_list)):
    folder_path = path_list[j]
    files = os.listdir(folder_path)
    for i, filename in enumerate(files):
        if filename.endswith(".jpg"):
            group_number = (i // 16) + 1
            file_number = (i % 16) + 1
            new_filename = f"{group_number}-{file_number}.jpg"
            old_filepath = os.path.join(folder_path, filename)
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(old_filepath, new_filepath)

print("success")
