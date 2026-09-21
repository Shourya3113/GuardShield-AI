import os
import shutil
from pathlib import Path

docs_dir = Path(r"d:\projects\GuardShield_AI\docs")

# First, rename files inside subdirectories
for root, dirs, files in os.walk(docs_dir, topdown=False):
    for f in files:
        if f == "README.md":
            continue
        if "_" in f:
            new_f = f.replace("_", " ")
            old_path = os.path.join(root, f)
            new_path = os.path.join(root, new_f)
            os.rename(old_path, new_path)
            print(f"File renamed: {f} -> {new_f}")

# Second, rename directories
for root, dirs, files in os.walk(docs_dir, topdown=False):
    for d in dirs:
        if "_" in d:
            new_d = d.replace("_", " ")
            old_path = os.path.join(root, d)
            new_path = os.path.join(root, new_d)
            os.rename(old_path, new_path)
            print(f"Dir renamed: {d} -> {new_d}")

print("Underscore replacement complete!")
