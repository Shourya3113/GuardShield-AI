import os
import shutil
from pathlib import Path

docs_dir = Path(r"d:\projects\GuardShield_AI\docs")

# Define target subdirectories
subdirs = {
    "01_Reports": docs_dir / "01_Reports",
    "02_Weekly_WPRs": docs_dir / "02_Weekly_WPRs",
    "03_Research_and_Catalogs": docs_dir / "03_Research_and_Catalogs",
    "04_Diagrams": docs_dir / "04_Diagrams",
    "05_Admin_and_Credentials": docs_dir / "05_Admin_and_Credentials"
}

for d in subdirs.values():
    d.mkdir(parents=True, exist_ok=True)

# Mapping of source filename to (target_subdir, new_filename)
file_mappings = {
    # 01_Reports
    "GuardShield_AI_Project_Progress_Report.docx": ("01_Reports", "Project_Progress_Report.docx"),
    "GuardShield_AI_Project_Progress_Report.md": ("01_Reports", "Project_Progress_Report.md"),
    "Project_Progress_Report.pdf": ("01_Reports", "Project_Progress_Report.pdf"),
    "GuardShield_AI_Amity_Project_Synopsis.docx": ("01_Reports", "Project_Synopsis.docx"),
    "GuardShield_AI_Presentation.pptx": ("01_Reports", "Presentation_Slides.pptx"),
    
    # 02_Weekly_WPRs
    "GuardShield_AI_WPR_Week_1.docx": ("02_Weekly_WPRs", "WPR_Week_1.docx"),
    "GuardShield_AI_WPR_Week_1.md": ("02_Weekly_WPRs", "WPR_Week_1.md"),
    "GuardShield_AI_WPR_Week_1_Brief.docx": ("02_Weekly_WPRs", "WPR_Week_1_Brief.docx"),
    "Minor Project WPR 1 (1).pdf": ("02_Weekly_WPRs", "WPR_Week_1.pdf"),
    "Minor Project WPR 2.pdf": ("02_Weekly_WPRs", "WPR_Week_2.pdf"),
    "GuardShield_AI_WPR_Week_3.docx": ("02_Weekly_WPRs", "WPR_Week_3.docx"),
    "GuardShield_AI_WPR_Week_3.md": ("02_Weekly_WPRs", "WPR_Week_3.md"),
    "Minor Project WPR 3.pdf": ("02_Weekly_WPRs", "WPR_Week_3.pdf"),
    "GuardShield_AI_WPR_Week_4.docx": ("02_Weekly_WPRs", "WPR_Week_4.docx"),
    "GuardShield_AI_WPR_Week_4.md": ("02_Weekly_WPRs", "WPR_Week_4.md"),
    "Minor Project WPR 4.pdf": ("02_Weekly_WPRs", "WPR_Week_4.pdf"),
    "GuardShield_AI_WPR_Week_5.docx": ("02_Weekly_WPRs", "WPR_Week_5.docx"),
    "GuardShield_AI_WPR_Week_5.md": ("02_Weekly_WPRs", "WPR_Week_5.md"),
    "MInor Project WPR 5.pdf": ("02_Weekly_WPRs", "WPR_Week_5.pdf"),
    
    # 03_Research_and_Catalogs
    "Published_Research_Datasets_Catalog.md": ("03_Research_and_Catalogs", "Published_Research_Datasets_Catalog.md"),
    "GuardShield_AI_DOI_Published_Datasets_Catalog.pdf": ("03_Research_and_Catalogs", "Published_Datasets_Catalog_with_DOIs.pdf"),
    "GuardShield_AI_Research_Gap_Formulation.pdf": ("03_Research_and_Catalogs", "Research_Gap_Formulation.pdf"),
    "GuardShield_AI_Original_Dataset_and_Research_Plan.pdf": ("03_Research_and_Catalogs", "Original_Dataset_and_Research_Plan.pdf"),
    "GuardShield_AI_Jury_QA_and_Research_Trends.pdf": ("03_Research_and_Catalogs", "Jury_QA_and_Research_Trends.pdf"),
    "GuardShield_AI_Complete_Pipeline_Guide.pdf": ("03_Research_and_Catalogs", "Complete_Pipeline_Guide.pdf"),
    "GuardShield_AI_Teammate_Beginners_Guide.pdf": ("03_Research_and_Catalogs", "Teammate_Beginners_Guide.pdf"),
    "Task_1_GuardShield_AI_Objectives_and_SubObjectives.docx": ("03_Research_and_Catalogs", "Objectives_and_SubObjectives.docx"),
    
    # 04_Diagrams
    "GuardShield_AI_WBS_Diagram.png": ("04_Diagrams", "WBS_Diagram.png"),
    
    # 05_Admin_and_Credentials
    "Abhishek Sir Sign_page-0001.jpg": ("05_Admin_and_Credentials", "Abhishek_Sir_Signature.jpg"),
    "Shourya Offer Letter (1).pdf": ("05_Admin_and_Credentials", "Shourya_Offer_Letter.pdf"),
    "Rachit Offer Letter (2).pdf": ("05_Admin_and_Credentials", "Rachit_Offer_Letter.pdf"),
    "Dhruv Offer Letter (2).pdf": ("05_Admin_and_Credentials", "Dhruv_Offer_Letter.pdf"),
    
    # Python scripts in docs (can be moved or cleaned)
    "build_wpr_docx.py": ("02_Weekly_WPRs", "build_wpr_docx.py"),
    "update_wpr_from_template.py": ("02_Weekly_WPRs", "update_wpr_from_template.py")
}

for src_name, (target_dir_key, new_name) in file_mappings.items():
    src_file = docs_dir / src_name
    target_file = subdirs[target_dir_key] / new_name
    if src_file.exists():
        shutil.move(str(src_file), str(target_file))
        print(f"Moved: {src_name} -> {target_dir_key}/{new_name}")

print("Docs organization complete!")
