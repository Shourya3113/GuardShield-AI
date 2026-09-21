import os
import shutil
from pathlib import Path

docs_dir = Path(r"d:\projects\GuardShield_AI\docs")

folder_renames = [
    ("Reports", "01 Reports"),
    ("Weekly WPRs", "02 Weekly WPRs"),
    ("Research and Catalogs", "03 Research and Catalogs"),
    ("Diagrams", "04 Diagrams"),
    ("Admin and Credentials", "05 Admin and Credentials")
]

for old_name, new_name in folder_renames:
    old_p = docs_dir / old_name
    new_p = docs_dir / new_name
    
    if old_p.exists() and not new_p.exists():
        old_p.rename(new_p)
        print(f"Renamed: {old_name} -> {new_name}")
    elif old_p.exists() and new_p.exists():
        # Move all files from old_p to new_p, then remove old_p
        for f in old_p.iterdir():
            dest = new_p / f.name
            shutil.move(str(f), str(dest))
            print(f"Moved {f.name} to {new_name}")
        old_p.rmdir()
        print(f"Removed redundant {old_name}")

print("\nFinal clean tree under docs:")
for root, dirs, files in os.walk(docs_dir):
    print(root, files)
