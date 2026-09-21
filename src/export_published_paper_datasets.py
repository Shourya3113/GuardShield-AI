import os
import sys
import json
import pandas as pd
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parent))
import config

def export_published_datasets():
    print("=" * 75)
    print("  [GuardShield AI] Expanding Published Research Datasets Catalog (12 Papers)")
    print("=" * 75)
    
    out_dir = config.DATA_DIR / "published_paper_datasets"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    published_catalog = [
        {
            "dataset_name": "JailbreakBench",
            "category": "Prompt Injection / Jailbreak",
            "paper_title": "JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models",
            "venue": "NeurIPS 2024 (Datasets & Benchmarks Track)",
            "publishing_entity": "University of Pennsylvania (UPenn)",
            "authors": "Patrick Chao, Alexander Robey, Edgar Dobriban, Hamed Hassani, George J. Pappas, Eric Wong",
            "doi": "10.52202/079017-1745",
            "paper_url": "https://arxiv.org/abs/2404.01318",
            "dataset_url": "https://huggingface.co/datasets/JailbreakBench/JBA-Artifacts"
        },
        {
            "dataset_name": "HackAPrompt",
            "category": "Prompt Injection / Jailbreak",
            "paper_title": "HackAPrompt: An Empirical Study of Prompt Injection Attacks on Large Language Models",
            "venue": "EMNLP 2023 (Findings)",
            "publishing_entity": "University of Maryland (UMD) & Scale AI",
            "authors": "Sander Schulhoff, Jeremy Pinto, Anaum Khan, Louis-François Bouchard, et al.",
            "doi": "10.18653/v1/2023.emnlp-main.982",
            "paper_url": "https://aclanthology.org/2023.emnlp-main.982/",
            "dataset_url": "https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset"
        },
        {
            "dataset_name": "AdvGLUE",
            "category": "Adversarial Robustness / Injection",
            "paper_title": "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models",
            "venue": "NeurIPS 2021",
            "publishing_entity": "UIUC & Microsoft Research",
            "authors": "Boxin Wang, Chejian Xu, Shuohang Wang, Zhe Gan, Yu Cheng, Jianfeng Gao, Ahmed Hassan Awadallah, Bo Li",
            "doi": "10.52202/060246-0315",
            "paper_url": "https://arxiv.org/abs/2111.09840",
            "dataset_url": "https://adversarialglue.github.io/"
        },
        {
            "dataset_name": "Do-Not-Answer",
            "category": "Safety Alignment / Harm Evaluation",
            "paper_title": "Do-Not-Answer: A Dataset for Evaluating Safeguards in Extreme Model Risk",
            "venue": "NeurIPS 2023",
            "publishing_entity": "MBZUAI & University of Melbourne",
            "authors": "Yuxia Wang, Haonan Li, Xudong Han, Preslav Nakov, Timothy Baldwin",
            "doi": "10.52202/075280-0442",
            "paper_url": "https://arxiv.org/abs/2308.13387",
            "dataset_url": "https://huggingface.co/datasets/LibrAI/do-not-answer"
        },
        {
            "dataset_name": "AutoDAN",
            "category": "Stealthy Automated Jailbreaks",
            "paper_title": "AutoDAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models",
            "venue": "ICLR 2024",
            "publishing_entity": "University of Wisconsin-Madison & UC Davis",
            "authors": "Xiaogeng Liu, Nan Xu, Muhao Chen, Chaowei Xiao",
            "doi": "10.48550/arXiv.2310.04451",
            "paper_url": "https://arxiv.org/abs/2310.04451",
            "dataset_url": "https://github.com/SheltonLiu-N/AutoDAN"
        },
        {
            "dataset_name": "BIPIA",
            "category": "Indirect Prompt Injection",
            "paper_title": "Benchmarking Indirect Prompt Injection Attacks on Large Language Models",
            "venue": "arXiv / Microsoft AI Safety Suite 2023",
            "publishing_entity": "Microsoft Research",
            "authors": "Jingwei Yi, Yueqi Xie, Fangzhao Wu, Jianfeng Gao, et al.",
            "doi": "10.48550/arXiv.2312.14197",
            "paper_url": "https://arxiv.org/abs/2312.14197",
            "dataset_url": "https://github.com/microsoft/BIPIA"
        },
        {
            "dataset_name": "BeaverTails",
            "category": "Safety Preference & Benign Baseline",
            "paper_title": "BeaverTails: Towards Improved Safety Alignment of LLM via Multi-Dimensional Preference Dataset",
            "venue": "NeurIPS 2023",
            "publishing_entity": "Peking University (PKU) & ETH Zürich",
            "authors": "Jiaming Ji, Mickel Liu, Josef Dai, Xuehai Pan, Chi Zhang, Ce Zhang, Yaodong Yang",
            "doi": "10.52202/075280-1072",
            "paper_url": "https://arxiv.org/abs/2307.04657",
            "dataset_url": "https://huggingface.co/datasets/PKU-Alignment/BeaverTails"
        },
        {
            "dataset_name": "HaluEval",
            "category": "Hallucination Benchmark",
            "paper_title": "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models",
            "venue": "EMNLP 2023",
            "publishing_entity": "Renmin University & Univ. de Montréal",
            "authors": "Junyi Li, Xiaoxue Cheng, Wayne Xin Zhao, Jian-Yun Nie, Ji-Rong Wen",
            "doi": "10.18653/v1/2023.emnlp-main.397",
            "paper_url": "https://aclanthology.org/2023.emnlp-main.397/",
            "dataset_url": "https://github.com/RUCAIBox/HaluEval"
        },
        {
            "dataset_name": "TruthfulQA",
            "category": "Hallucination & Factuality",
            "paper_title": "TruthfulQA: Measuring How Models Mimic Human Falsehoods",
            "venue": "ACL 2022",
            "publishing_entity": "University of Oxford & OpenAI",
            "authors": "Stephanie Lin, Jacob Hilton, Owain Evans",
            "doi": "10.18653/v1/2022.acl-long.229",
            "paper_url": "https://aclanthology.org/2022.acl-long.229/",
            "dataset_url": "https://huggingface.co/datasets/truthfulqa/truthful_qa"
        },
        {
            "dataset_name": "FEVER",
            "category": "Fact Extraction & NLI Entailment",
            "paper_title": "FEVER: A Large-Scale Dataset for Fact Extraction and VERification",
            "venue": "NAACL-HLT 2018",
            "publishing_entity": "University of Cambridge & Amazon",
            "authors": "James Thorne, Andreas Vlachos, Christos Christodoulopoulos, Arpit Mittal",
            "doi": "10.18653/v1/N18-1074",
            "paper_url": "https://aclanthology.org/N18-1074/",
            "dataset_url": "https://fever.ai/resources.html"
        },
        {
            "dataset_name": "FaithDial",
            "category": "Factual Grounding & Hallucination",
            "paper_title": "FaithDial: A Faithful Benchmark for Information-Seeking Dialogue",
            "venue": "ACL 2022",
            "publishing_entity": "McGill University, Mila & Univ. of Alberta",
            "authors": "Nouha Dziri, Ehsan Kamalloo, Sivan Milton, Osmar Zaiane, Mo Yu, Edoardo M. Ponti, Siva Reddy",
            "doi": "10.18653/v1/2022.trans-acl.1.72",
            "paper_url": "https://aclanthology.org/2022.trans-acl.1.72/",
            "dataset_url": "https://huggingface.co/datasets/McGill-NLP/FaithDial"
        },
        {
            "dataset_name": "KoLA",
            "category": "World Knowledge & Hallucination",
            "paper_title": "KoLA: Carefully Benchmarking World Knowledge of Large Language Models",
            "venue": "ICLR 2024",
            "publishing_entity": "Tsinghua University",
            "authors": "Jifan Yu, Xiaozhi Wang, Shangqing Tu, Shulin Cao, Daniel Zhang-Li, Xin Lv, Hao Peng, et al.",
            "doi": "10.48550/arXiv.2306.09296",
            "paper_url": "https://arxiv.org/abs/2306.09296",
            "dataset_url": "https://github.com/THU-KEG/KoLA"
        }
    ]
    
    # Save as JSON
    json_path = out_dir / "published_research_paper_datasets.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(published_catalog, f, indent=2, ensure_ascii=False)
        
    # Save as CSV
    csv_path = out_dir / "published_research_paper_datasets.csv"
    df = pd.DataFrame(published_catalog)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    print(f"  [OK] Exported {len(published_catalog)} published datasets to JSON -> {json_path}")
    print(f"  [OK] Exported {len(published_catalog)} published datasets to CSV  -> {csv_path}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    export_published_datasets()
