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
    except Exception as e:
        return None

def find_and_remove_duplicates():
    downloads_dir = Path(os.path.expanduser("~/Downloads"))
    project_dir = Path(r"d:\projects\GuardShield_AI")
    
    # 1. Compute hashes for all files in project repository
    print("Hashing all files in project repository...")
    project_hashes = {} # hash -> list of project file paths
    project_files_count = 0
    
    for root, dirs, files in os.walk(project_dir):
        # Skip git or cache dirs
        if ".git" in root or "__pycache__" in root or ".venv" in root:
            continue
        for f in files:
            full_path = Path(root) / f
            f_hash = get_file_hash(full_path)
            if f_hash:
                if f_hash not in project_hashes:
                    project_hashes[f_hash] = []
                project_hashes[f_hash].append(full_path)
                project_files_count += 1
                
    print(f"Total project files indexed: {project_files_count}")
    
    # 2. Check files in Downloads
    print("\nScanning Downloads folder for duplicates...")
    duplicates_to_delete = []
    
    for root, dirs, files in os.walk(downloads_dir):
        # Avoid non-document internal directories if any
        if "node_modules" in root or ".git" in root:
            continue
        for f in files:
            full_path = Path(root) / f
            f_hash = get_file_hash(full_path)
            if f_hash and f_hash in project_hashes:
                matching_project_files = project_hashes[f_hash]
                duplicates_to_delete.append((full_path, matching_project_files))
                
    print(f"\nFound {len(duplicates_to_delete)} exact duplicate files in Downloads:")
    for dl_file, proj_files in duplicates_to_delete:
        proj_str = ", ".join([str(p.relative_to(project_dir)) for p in proj_files])
        print(f" • [DOWNLOADS] {dl_file.name}")
        print(f"   Matches project file(s): {proj_str}")
        
    # 3. Delete exact duplicates from Downloads
    deleted_count = 0
    for dl_file, _ in duplicates_to_delete:
        try:
            os.remove(dl_file)
            deleted_count += 1
            print(f"Deleted: {dl_file}")
        except Exception as e:
            print(f"Failed to delete {dl_file}: {e}")
            
    print(f"\nSuccessfully cleaned up {deleted_count} duplicate files from Downloads!")

if __name__ == "__main__":
    find_and_remove_duplicates()
