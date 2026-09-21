import os
import sys
import json
import shutil
import pandas as pd
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def export_csv_files():
    root = Path(r"d:\projects\GuardShield_AI")
    downloads = Path(os.path.expanduser(r"~\Downloads"))
    
    # 1. Export GuardShield_Bench_v1.csv (451 records)
    bench_json = root / "data" / "processed" / "guardshield_bench_v1.json"
    with open(bench_json, "r", encoding="utf-8") as f:
        bench_data = json.load(f)
        
    for item in bench_data:
        item["label_name"] = "Malicious Attack" if item.get("label") == 1 else "Safe / Benign Prompt"
        
    df_bench = pd.DataFrame(bench_data)
    
    # Reorder columns for clean presentation
    cols = ["prompt", "label", "label_name", "attack_type", "source"]
    existing_cols = [c for c in cols if c in df_bench.columns]
    df_bench = df_bench[existing_cols]
    
    out_bench_csv1 = root / "data" / "processed" / "GuardShield_Bench_v1.csv"
    out_bench_csv2 = root / "docs" / "03 Research and Catalogs" / "GuardShield_Bench_v1.csv"
    out_bench_downloads = downloads / "GuardShield_Bench_v1.csv"
    
    df_bench.to_csv(out_bench_csv1, index=False, encoding="utf-8-sig")
    df_bench.to_csv(out_bench_csv2, index=False, encoding="utf-8-sig")
    df_bench.to_csv(out_bench_downloads, index=False, encoding="utf-8-sig")
    print(f"[OK] Exported GuardShield_Bench_v1.csv ({len(df_bench)} rows)")

    # 2. Export Test Split CSV (46 unseen test records)
    test_json = root / "data" / "processed" / "splits" / "test.json"
    with open(test_json, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    for item in test_data:
        item["label_name"] = "Malicious Attack" if item.get("label") == 1 else "Safe / Benign Prompt"
    df_test = pd.DataFrame(test_data)
    df_test = df_test[[c for c in cols if c in df_test.columns]]
    
    out_test_csv = root / "data" / "processed" / "splits" / "test.csv"
    out_test_downloads = downloads / "GuardShield_Test_Split_46_Samples.csv"
    df_test.to_csv(out_test_csv, index=False, encoding="utf-8-sig")
    df_test.to_csv(out_test_downloads, index=False, encoding="utf-8-sig")
    print(f"[OK] Exported test.csv ({len(df_test)} rows)")

    # 3. Export Published Research Paper Datasets Catalog CSV (12 papers)
    pub_csv = root / "data" / "published_paper_datasets" / "published_research_paper_datasets.csv"
    out_pub_docs = root / "docs" / "03 Research and Catalogs" / "Published_Research_Paper_Datasets.csv"
    out_pub_downloads = downloads / "GuardShield_Published_Datasets_Catalog.csv"
    
    if pub_csv.exists():
        shutil.copy(str(pub_csv), str(out_pub_docs))
        shutil.copy(str(pub_csv), str(out_pub_downloads))
        print(f"[OK] Exported Published_Research_Paper_Datasets.csv (12 papers)")

    print("\nAll CSV datasets successfully created and placed in Downloads & Project Docs!")

if __name__ == "__main__":
    export_csv_files()
