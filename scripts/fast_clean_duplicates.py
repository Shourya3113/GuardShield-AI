import os
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def fast_clean_duplicates():
    downloads_dir = Path(os.path.expanduser("~/Downloads"))
    project_docs = Path(r"d:\projects\GuardShield_AI\docs")
    
    # 1. Index all files inside project docs
    print("Indexing all files in d:\\projects\\GuardShield_AI\\docs...")
    project_hashes = {}
    
    for root, dirs, files in os.walk(project_docs):
        for f in files:
            full_p = Path(root) / f
            h = get_file_hash(full_p)
            if h:
                if h not in project_hashes:
                    project_hashes[h] = []
                project_hashes[h].append(full_p)
                
    print(f"Total project doc files indexed: {len(project_hashes)} unique hashes.")
    
    # 2. Check top-level files in Downloads only
    print("\nScanning top-level files in Downloads...")
    deleted_files = []
    
    for item in downloads_dir.iterdir():
        if item.is_file():
            # Skip hidden files or downloads in progress
            if item.name.startswith(".") or item.suffix in [".crdownload", ".tmp"]:
                continue
            h = get_file_hash(item)
            if h and h in project_hashes:
                matching_docs = project_hashes[h]
                match_str = ", ".join([str(p.name) for p in matching_docs])
                try:
                    os.remove(item)
                    deleted_files.append((item.name, match_str))
                    print(f"Deleted duplicate from Downloads: {item.name} -> Matches: {match_str}")
                except Exception as e:
                    print(f"Error deleting {item.name}: {e}")
                    
    print("\n" + "=" * 65)
    print(f"  Summary: Deleted {len(deleted_files)} duplicate files from Downloads:")
    for dl_name, m in deleted_files:
        print(f"  • {dl_name} (Matches: {m})")
    print("=" * 65)

if __name__ == "__main__":
    fast_clean_duplicates()
