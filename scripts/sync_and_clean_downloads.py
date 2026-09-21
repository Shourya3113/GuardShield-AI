import os
import shutil
from pathlib import Path

downloads_dir = Path(os.path.expanduser("~/Downloads"))
docs_dir = Path(r"d:\projects\GuardShield_AI\docs")

# Mapping of downloads files to target subfolders in docs with clean names
clean_mappings = {
    "GuardShield_AI_Amity_Project_Synopsis.pdf": ("01 Reports", "Project Synopsis.pdf"),
    "GuardShield_AI_Presentation.pptx": ("01 Reports", "Presentation Slides.pptx"),
    "GuardShield_AI_Complete_Pipeline_Guide.pdf": ("03 Research and Catalogs", "Complete Pipeline Guide.pdf"),
    "GuardShield_AI_Complete_Project_and_Research_Guide.pdf": ("03 Research and Catalogs", "Complete Project and Research Guide.pdf"),
    "GuardShield_AI_DOI_Published_Datasets_Catalog.pdf": ("03 Research and Catalogs", "Published Datasets Catalog with DOIs.pdf"),
    "GuardShield_AI_Jury_QA_and_Research_Trends.pdf": ("03 Research and Catalogs", "Jury QA and Research Trends.pdf"),
    "GuardShield_AI_Original_Dataset_and_Research_Plan.pdf": ("03 Research and Catalogs", "Original Dataset and Research Plan.pdf"),
    "GuardShield_AI_Project_Proposal.pdf": ("01 Reports", "Project Proposal.pdf"),
    "GuardShield_AI_Research_Gap_Formulation.pdf": ("03 Research and Catalogs", "Research Gap Formulation.pdf"),
    "GuardShield_AI_Teammate_Beginners_Guide.pdf": ("03 Research and Catalogs", "Teammate Beginners Guide.pdf"),
    "Task_1_GuardShield_AI_Objectives_and_SubObjectives.pdf": ("03 Research and Catalogs", "Objectives and SubObjectives.pdf"),
}

deleted_from_downloads = []

for src_name, (target_subdir, clean_name) in clean_mappings.items():
    src_path = downloads_dir / src_name
    dest_path = docs_dir / target_subdir / clean_name
    
    if src_path.exists():
        # Ensure it is safely backed up in project docs first
        if not dest_path.exists():
            shutil.copy2(str(src_path), str(dest_path))
            print(f"Copied to project docs: {src_name} -> docs/{target_subdir}/{clean_name}")
        else:
            print(f"Already verified in project docs: docs/{target_subdir}/{clean_name}")
            
        # Delete from Downloads
        try:
            os.remove(src_path)
            deleted_from_downloads.append((src_name, f"docs/{target_subdir}/{clean_name}"))
            print(f"Deleted from Downloads: {src_name}")
        except Exception as e:
            print(f"Failed to delete {src_name}: {e}")

print("\n" + "=" * 65)
print(f"  Summary: Processed and deleted {len(deleted_from_downloads)} project files from Downloads:")
for dl_f, proj_f in deleted_from_downloads:
    print(f"  • {dl_f} -> Preserved in: {proj_f}")
print("=" * 65)
