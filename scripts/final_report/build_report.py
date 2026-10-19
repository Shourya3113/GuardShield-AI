"""
Builds the NTCC (ETMN100) final project report as a Word document, following the Amity guideline
(docs: MINOR PROJECT (ETMN 100).pdf): preliminary pages, chapters, references, appendices.

  python scripts/final_report/make_figures.py
  python scripts/final_report/build_report.py           # writes the .docx and, through Word, the .pdf

Every number comes from committed result files: docs/01 Reports/*.json (GuardShield system) and
paper1/paper/generated/*.tex (the research study, built by paper1/paper/make_assets.py).
"""

import json
import re
import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_docx import Report  # noqa: E402

BASE = Path(__file__).resolve().parents[2]
REP = BASE / "docs" / "01 Reports"
OUTDIR = REP / "Final Project Report"
FIG = OUTDIR / "figures"
PFIG = BASE / "paper1" / "paper" / "generated"

TITLE = "GuardShield AI: A Real-Time Sidecar Proxy for Prompt-Injection Defense and Hallucination Detection, with an Audit of Format-Triggered Over-Defense in Prompt-Injection Detectors"
STUDENTS = [("Shourya Solanki", "A2305223569"), ("Rachit Ryan Chug", "A2305223166"), ("Dhruv Raj Singh", "A2305223191")]
GUIDE = "Dr. Abhishek Kaushal"
STUDENT_DEPT = "Amity School of Engineering and Technology (ASET)"  # the students' department
GUIDE_DEPT = "Amity Centre of Artificial Intelligence (ACAI)"  # the guide's department
PROGRAMME = "Computer Science and Engineering (Artificial Intelligence and Machine Learning)"
MONTH = "October 2026"


def load(name):
    return json.loads((REP / f"{name}.json").read_text(encoding="utf-8"))


def macros():
    out = {}
    for f in PFIG.glob("numbers*.tex"):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}$", line.strip())
            if m:
                out[m.group(1)] = m.group(2).replace("{,}", ",")
    return out


R1, R2, R3, R4 = (load("raw_eval_in_distribution_test_698"), load("raw_eval_out_of_distribution_500"),
                  load("raw_eval_stage2_factuality_800"), load("raw_eval_pipeline_e2e"))
PAI, TF, MT = load("table_external_baseline_protectai"), load("table_tfidf_baseline_comparison"), load("table_multiturn_benchmark")
M = macros()


def pct(x, nd=2):
    return f"{100 * x:.{nd}f}%"


def cm(d):
    return d["metrics"]["confusion_matrix"] if "metrics" in d else d["confusion_matrix"]


# ===================================================================== preliminary pages
def title_page(r):
    def line(text, size=12, bold=False, before=0, after=6, italic=False):
        p = r.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        run = p.add_run(text)
        run.bold, run.italic = bold, italic
        run.font.size = Pt(size)
        return p
    line("A Project Report", 14, before=6)
    line("On", 12)
    line(TITLE, 15, bold=True, after=12)
    line("Submitted to", 12)
    line("Amity University Uttar Pradesh", 13, bold=True, after=10)
    logo = OUTDIR / "figures" / "amity_logo.png"
    if logo.exists():
        p = r.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.add_run().add_picture(str(logo), width=Inches(1.3))
    line("in partial fulfillment of the requirements for the award of the degree of", 12, before=6, italic=True)
    line("Bachelor of Technology", 13, bold=True, after=0)
    line(PROGRAMME, 12, after=10)
    line("by", 12)
    for name, enr in STUDENTS:
        line(f"{name} ({enr})", 12, bold=True, after=0)
    line("under the guidance of", 12, before=10)
    line(GUIDE, 13, bold=True, after=12)
    line(STUDENT_DEPT.upper(), 12, bold=True, after=0)
    line("AMITY UNIVERSITY UTTAR PRADESH", 12, bold=True, after=0)
    line("NOIDA (U.P.)", 12, after=10)
    line(MONTH, 12)


def declaration(r):
    r.heading("DECLARATION", 1)
    names = ", ".join(n for n, _ in STUDENTS[:-1]) + f" and {STUDENTS[-1][0]}"
    r.para(f"We, {names}, students of B.Tech ({PROGRAMME}), hereby declare that the project titled "
           f"\u201c{TITLE}\u201d, which is submitted by us to {STUDENT_DEPT}, Amity University "
           f"Uttar Pradesh, Noida, in partial fulfillment of the requirement for the award of the degree of Bachelor of "
           f"Technology in {PROGRAMME}, has not previously formed the basis for the award of any degree, diploma or "
           f"other similar title or recognition.")
    r.para("")
    r.para("Noida", indent=False)
    r.para("Date: ____________", indent=False)
    r.para("")
    for name, enr in STUDENTS:
        r.para(f"{name} ({enr})          Signature: ____________________", indent=False, align=WD_ALIGN_PARAGRAPH.RIGHT)


def certificate(r):
    r.page_break()
    r.heading("CERTIFICATE", 1)
    names = ", ".join(n for n, _ in STUDENTS[:-1]) + f" and {STUDENTS[-1][0]}"
    r.para(f"On the basis of the declaration submitted by {names}, students of B.Tech ({PROGRAMME}), I hereby certify "
           f"that the project titled \u201c{TITLE}\u201d, which is submitted to {STUDENT_DEPT}, "
           f"Amity University Uttar Pradesh, Noida, in partial fulfillment of the requirement for the award of the degree "
           f"of Bachelor of Technology in {PROGRAMME}, is an original contribution with existing knowledge and a faithful "
           f"record of work carried out by them under my guidance and supervision.")
    r.para("To the best of my knowledge this work has not been submitted in part or full for any degree or diploma to "
           "this University or elsewhere.")
    r.para("")
    r.para("Noida", indent=False)
    r.para("Date: ____________", indent=False)
    for t in (GUIDE, "(Guide)", GUIDE_DEPT, "Amity University Uttar Pradesh, Noida"):
        r.para(t, indent=False, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)


def acknowledgement(r):
    r.page_break()
    r.heading("ACKNOWLEDGEMENT", 1)
    r.para(f"We express our sincere gratitude to our project guide, {GUIDE}, {GUIDE_DEPT}, for "
           "his continuous guidance, critical feedback and encouragement throughout this project. His suggestion to aim "
           "for a research publication shaped the second half of the work.")
    r.para("We thank the Head of the Department and the NTCC committee for the opportunity to carry out this project, "
           "and the faculty of the department for their support during the progress reviews.")
    r.para("We acknowledge the open-source community whose models, datasets and tools made this work possible, in "
           "particular the maintainers of Hugging Face Transformers, PyTorch and the public benchmarks cited in this "
           "report, and Kaggle for free GPU time.")
    r.para("[To be reviewed by the team: Generative AI tools (Anthropic's Claude) were used to assist with code review, "
           "experiment scripting and editing of drafts. All experiments were run, checked and interpreted by the team, "
           "and every reported number is reproduced from the committed result files. Keep, adjust or remove this "
           "sentence according to the University's policy on AI assistance.]", italic=True)
    r.para("")
    for name, _ in STUDENTS:
        r.para(name, indent=False, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)


def contents_pages(r):
    for title, code in (("TABLE OF CONTENTS", 'TOC \\o "1-3" \\h \\z \\u'),
                        ("LIST OF TABLES", 'TOC \\h \\z \\t "Table Caption,1"'),
                        ("LIST OF FIGURES", 'TOC \\h \\z \\t "Figure Caption,1"')):
        r.page_break()
        p = r.para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, space_after=12)
        r.toc(code)


def abstract(r):
    r.page_break()
    r.heading("ABSTRACT", 1)
    m1, m2, m3 = R1["metrics"], R2["metrics"], R3["metrics"]
    r.para("Applications built on large language models (LLMs) face two failures that ordinary software does not: "
           "prompt injection, where text supplied by a user or a retrieved document overrides the developer's "
           "instructions, and hallucination, where the model states unsupported facts with confidence. This project "
           "builds GuardShield AI, a sidecar proxy that sits in front of an OpenAI-compatible LLM endpoint and checks "
           "both the incoming prompt and the outgoing answer in real time.")
    r.para(f"Stage 1 is a fine-tuned DeBERTa-v3-small classifier with sliding-window chunking. On a held-out test set of "
           f"698 prompts it reaches {pct(m1['accuracy'])} accuracy with a {pct(m1['fpr'])} false-positive rate, and on 500 "
           f"zero-shot out-of-distribution prompts {pct(m2['accuracy'])} accuracy, at a median latency of "
           f"{m1['latency_p50_ms']:.1f} ms. Stage 2 is a cross-encoder natural-language-inference verifier that checks a "
           f"generated claim against retrieved evidence; on 800 FEVER and HaluEval pairs it reaches {pct(m3['accuracy'])} "
           f"accuracy (AUROC {m3['auroc']:.3f}). A streaming entropy monitor can halt generation when token uncertainty "
           f"spikes, and HMAC-signed conversation history lowers false alarms in multi-turn chats. The full pipeline adds "
           f"a median of {R4['metrics']['latency_p50_ms']:.1f} ms per request on a 4 GB laptop GPU.")
    r.para(f"While evaluating the classifier, the team found that robustness tests for such detectors only perturb "
           f"attacks. The research part of the project therefore audits {M['nGuards']} open detectors with a paired "
           f"protocol in which every attack and a length-matched benign twin receive the identical obfuscation. The "
           f"detectors lose the ability to separate attacks from benign text in {M['nSigDestroyed']} of {M['nCells']} "
           f"detector\u2013perturbation cells, and {M['pctAttackRobustFC']}% of the cells that look robust on attacks alone "
           f"keep their recall only by also blocking the benign twin. The cause is traced to each detector's tokenizer. "
           f"Script-aware input canonicalization restores much of the lost signal (AUROC {M['scPidsNoneSeenCharAuc']} to "
           f"{M['scPidsScriptAwareSeenCharAuc']}), whereas retraining on perturbed data reaches {M['scPidsAugmentSeenCharAuc']} "
           f"on a new data source. The study is written up as a research paper in IEEE conference format.")
    r.para("**Keywords:** prompt injection, LLM guardrails, hallucination detection, natural language inference, "
           "robustness evaluation, Unicode canonicalization.", indent=False)


# ========================================================================== chapters
def ch_introduction(r):
    r.chapter_heading("Introduction")
    r.section("1.1 Purpose of the Project")
    r.para("Large language models are now used as the reasoning core of chat assistants, coding tools, customer-support "
           "agents and retrieval-augmented question answering. Their input is natural language, which means that the "
           "boundary between data and instructions is blurred: any text the model reads can try to change what it does. "
           "Their output is also natural language, produced by sampling, which means a fluent answer is not necessarily "
           "a correct one.")
    r.para("The purpose of this project is to give developers a practical, open and measurable safety layer for such "
           "systems. GuardShield AI is designed as a *sidecar*: a separate service that the application calls instead of "
           "the LLM, which forwards safe requests to the model and checks its answers, without changing the application "
           "or the model. The project also asks a research question that arose during its evaluation: are the "
           "robustness numbers reported for prompt-injection detectors, including our own, actually measuring "
           "robustness?")
    r.section("1.2 Background and Available Alternatives")
    r.para("**Prompt injection** was first described for instruction-following models as \u201cgoal hijacking\u201d and prompt "
           "leaking (Perez and Ribeiro, 2022). Indirect prompt injection extends the threat to text the model retrieves "
           "rather than text the user types, such as web pages, e-mails or documents (Greshake et al., 2023). Attackers "
           "also hide instructions with character tricks and encodings, for example zero-width characters, homoglyphs, "
           "leetspeak or Base64 (Hackett et al., 2025).")
    r.para("**Hallucination** detection has followed two routes. Sampling-based methods such as SelfCheckGPT generate "
           "several answers and treat disagreement as a warning sign (Manakul et al., 2023), which multiplies inference "
           "cost. Uncertainty-based methods inspect the model's own probabilities, for example semantic entropy (Kuhn et "
           "al., 2023). Evidence-based methods compare the answer with retrieved sources, which is the setting of fact "
           "verification benchmarks such as FEVER (Thorne et al., 2018) and HaluEval (Li et al., 2023).")
    r.para("The available alternatives for a developer fall into three groups, compared in Table 1.1.")
    r.table(["Alternative", "Examples", "Strength", "Limitation"],
            [["Large LLM judges", "Llama Guard 3/4, Qwen3Guard, WildGuard", "Broad harm policy", "1\u201312 B parameters; high latency; trained for harmfulness, not injection"],
             ["Small encoder classifiers", "ProtectAI DeBERTa v2, Prompt Guard 2, deepset", "Fast, cheap", "Brittle under obfuscation; over-blocking"],
             ["Commercial APIs", "Lakera Guard, Azure Prompt Shields", "Managed service", "Closed, paid, data leaves the premises, not reproducible"],
             ["GuardShield AI (this project)", "DeBERTa-v3-small + NLI + entropy", "Open, ~26 ms, input and output checks", "Must be measured honestly against the same failure modes"]],
            "Alternatives for securing an LLM application", widths=[1.35, 1.6, 1.15, 1.65])
    r.section("1.3 Problem Statement")
    r.para("Build an open, low-latency proxy that (i) blocks prompt injections and jailbreaks before they reach the LLM, "
           "(ii) flags generated claims that contradict the available evidence, and (iii) does so with measured, "
           "reproducible accuracy, false-positive rate and latency on public benchmarks. In addition, determine whether "
           "standard robustness evaluations of prompt-injection detectors can tell a robust detector from one that simply "
           "blocks every unusual-looking input, and which remedy restores the detector's discrimination.")
    r.section("1.4 Project Goals and Objectives")
    r.bullets([
        "Fine-tune a small transformer classifier that detects prompt injections with high recall and a low false-positive rate, in under 50 ms on a laptop GPU.",
        "Build a fact-grounding verifier that checks generated claims against retrieved evidence and separates contradiction from mere lack of evidence.",
        "Integrate both stages, a streaming entropy monitor and multi-turn conversation handling into an OpenAI-compatible FastAPI proxy.",
        "Evaluate every component on public benchmarks with confidence intervals, per-sample logs and data provenance (dataset and weight hashes).",
        "Audit 19 open detectors with a paired benign-twin protocol, explain their failures, and compare canonicalization with retraining as remedies.",
        "Publish the research outcome as a paper, as required by the NTCC guidelines.",
    ])
    r.section("1.5 Organization of the Report")
    r.para("Chapter 2 defines the scope, budget and constraints, and Chapter 3 the requirements. Chapter 4 reviews the "
           "literature. Chapter 5 describes the system design and the research methodology, and Chapter 6 presents the "
           "results. Chapters 7 and 8 cover project management and risk. Chapter 9 discusses limitations and future "
           "scope, Chapter 10 concludes, and Chapter 11 records individual contributions. References and appendices "
           "follow.")


def ch_scope(r):
    r.chapter_heading("Scope and Constraints")
    r.section("2.1 Scope Definition")
    r.para("The project covers the design, implementation and evaluation of GuardShield AI and the research audit that "
           "grew out of it. In scope:")
    r.bullets([
        "Stage 1 prompt-injection classifier: data curation from public corpora, training, decontamination and evaluation.",
        "Stage 2 fact verifier based on a pretrained NLI cross-encoder, with sentence-aligned evidence windows.",
        "Streaming entropy monitor for token-level uncertainty during generation.",
        "FastAPI sidecar proxy with an OpenAI-compatible chat endpoint, multi-turn scanning and HMAC-signed assistant history.",
        "Evaluation harness, comparison with ProtectAI DeBERTa-v3 and a TF-IDF baseline, and latency measurement.",
        "Research audit (Study 1) of 19 detectors on two attack sources, with a contamination audit and a tokenizer-level explanation.",
        "Mitigation study (Study 2): canonicalization versus benign-twin augmentation, five training seeds per arm.",
    ])
    r.para("Out of scope: training a new LLM; defending against attackers who adapt to GuardShield specifically; "
           "commercial APIs (excluded for cost, terms of service and reproducibility); and the Hindi / Hinglish benchmark, "
           "which was moved to the eighth-semester project because writing native-speaker text in three scripts for 400 "
           "prompts was too large for this semester.")
    r.section("2.2 Projected Budget")
    r.para("The project was planned and completed with no expenditure, as summarised in Table 2.1.")
    r.table(["Item", "Source", "Cost (INR)"],
            [["Laptop with NVIDIA RTX 3050 (4 GB)", "Team member's own machine", "0"],
             ["Cloud GPU (2 \u00d7 NVIDIA T4, about 30 GPU-hours per week)", "Kaggle free tier", "0"],
             ["Models (DeBERTa-v3, NLI cross-encoder, 19 audited detectors)", "Hugging Face Hub, open licences", "0"],
             ["Datasets (SPML, deepset, Gandalf, Dolly, PIDS-Bench, FEVER, HaluEval, Aya)", "Public research releases", "0"],
             ["Software (Python, PyTorch, Transformers, FastAPI, Overleaf)", "Open source / free tier", "0"],
             ["**Total**", "", "**0**"]],
            "Projected and actual budget", widths=[3.0, 1.9, 0.85])
    r.section("2.3 Project Constraints")
    r.bullets([
        "**Hardware:** a 4 GB laptop GPU limits model size; the 8\u201312 B judges were scored on Kaggle, and retraining used the small DeBERTa backbone only.",
        "**Time:** 12 weeks within the NTCC calendar (commencement 20 July 2026, end date 9 October 2026, final report 26 October 2026).",
        "**Licences and gating:** several detectors (Llama Guard, Prompt Guard, Sentinel) require licence acceptance on Hugging Face; one (PIGuard) executes remote code and was not enabled.",
        "**Data:** only public data with known licences; no personal data; PIDS-Bench is restricted to research use.",
        "**Reproducibility:** every reported number had to be regenerated from committed files, with pinned model revisions and dataset hashes.",
        "**Plagiarism:** the report must stay below a 15% similarity index (Turnitin).",
    ])


def ch_requirements(r):
    r.chapter_heading("Requirement Analysis")
    r.section("3.1 Functional Requirements")
    r.table(["ID", "Requirement"],
            [["FR1", "Accept OpenAI-compatible /v1/chat/completions requests and forward safe ones to a configurable upstream LLM."],
             ["FR2", "Score every user message for prompt injection and block requests with risk at or above 0.5 (HTTP 403)."],
             ["FR3", "Scan long prompts with sliding windows so that padding cannot hide an attack beyond the first window."],
             ["FR4", "Scan multi-turn conversations, using short previous turns as context, and skip assistant turns signed by the proxy."],
             ["FR5", "Reject oversized payloads (HTTP 413) before inference."],
             ["FR6", "Monitor token entropy during streaming and stop generation after consecutive uncertainty spikes."],
             ["FR7", "Verify a generated claim against evidence: entailed, contradicted (flag) or neutral (unverified)."],
             ["FR8", "Provide an audit harness that builds paired datasets, scores any configured detector, computes metrics and writes reports."],
             ["FR9", "Record provenance for every result: dataset SHA-256, weights SHA-256, model revision, git commit, device."]],
            "Functional requirements", widths=[0.6, 5.15])
    r.section("3.2 Non-Functional Requirements")
    r.table(["Category", "Requirement", "Achieved"],
            [["Latency", "Stage 1 median under 50 ms on a laptop GPU", f"{R1['metrics']['latency_p50_ms']:.1f} ms"],
             ["Latency", "Full pipeline median under 100 ms", f"{R4['metrics']['latency_p50_ms']:.1f} ms"],
             ["Accuracy", "Stage 1 false-positive rate under 2% on held-out benign prompts", pct(R1['metrics']['fpr'])],
             ["Resources", "Run inference on a 4 GB GPU or CPU", "Yes"],
             ["Security", "Signed history with a secret key; no secret in code", "HMAC-SHA256, key from environment"],
             ["Reproducibility", "Results regenerate from committed files", "Pinned revisions, hashes, scripts"],
             ["Maintainability", "Automated tests in continuous integration", "40 tests"],
             ["Licensing", "Open-source release", "Apache-2.0"]],
            "Non-functional requirements", widths=[1.2, 3.0, 1.55])
    r.section("3.3 Hardware and Software Requirements")
    r.bullets([
        "Hardware: x86-64 machine, 8 GB RAM or more; NVIDIA GPU with 4 GB memory recommended (CPU works at lower speed).",
        "Software: Python 3.10+, PyTorch 2.6, Hugging Face Transformers 4.57, FastAPI, scikit-learn, NumPy and pandas.",
        "Cloud (research audit only): Kaggle notebook with 2 \u00d7 T4 GPUs for the 8\u201312 B parameter judges.",
    ])


def ch_literature(r):
    r.chapter_heading("Literature Review")
    r.para("The review is organised by theme. It covers the threat, the detectors deployed against it, how those "
           "detectors are evaluated, hallucination detection, and the remedies proposed for obfuscation. The research "
           "gap is stated at the end.")
    r.section("4.1 Prompt Injection and Jailbreaks")
    r.para("Perez and Ribeiro (2022) showed that simple instructions such as \u201cignore previous instructions\u201d hijack "
           "an instruction-following model and leak its system prompt. Greshake et al. (2023) showed that the same attack "
           "works indirectly, through retrieved web pages and documents, which makes every LLM-integrated application "
           "that reads untrusted text a target. Public attack corpora used in this project come from this line of work: "
           "the SPML benchmark of system-prompt attacks (Sharma et al., 2024), the deepset prompt-injection dataset "
           "(deepset, 2023) and the Gandalf game, in which players tried to make a model reveal a password (Lakera AI, 2023).")
    r.section("4.2 Detectors and Guard Models")
    r.para("Two families of detectors are deployed. Fine-tuned encoder classifiers, such as ProtectAI's DeBERTa-v3 model, "
           "Meta's Prompt Guard 2 (Meta, 2025) and PIGuard (Li et al., 2025), are small and fast. Generative safety judges "
           "such as Llama Guard (Inan et al., 2023), Qwen3Guard (Zhao et al., 2025) and WildGuard (Han et al., 2024) apply "
           "a broad harm policy but are large and slow. HiveTraceGuard-Pro is a compact generative guard trained on "
           "obfuscated examples of both labels (Oblakov et al., 2026). GuardShield's Stage 1 builds on DeBERTa-v3 (He et "
           "al., 2023), the backbone of most encoder detectors.")
    r.section("4.3 Evaluation of Detectors")
    r.para("Li et al. (2025) introduced NotInject and defined over-defense as false alarms caused by trigger words in "
           "benign prompts. PIDS-Bench evaluates four detectors on in-distribution, out-of-distribution and obfuscated "
           "data, but its obfuscated set contains attacks only, so the false-positive rate under obfuscation is "
           "undefined (Shire and Kim, 2026). Liu (2026) audits 15 detectors on benign agent tool outputs, finds "
           "default-threshold false-positive rates from 0% to 93%, and shows that one detector was trained on the "
           "benchmark used to evaluate it. Fairoze et al. (2026) report that Prompt Guard 2 regresses on encoded attacks. "
           "Hackett et al. (2025) measure evasion of six guards under character injection, again on attacks only.")
    r.para("Zhang et al. (2026) make the decisive methodological point for chat models: a model that refuses every "
           "encoded request looks safe if only harmful requests are encoded. They add benign requests under the same "
           "encoding and a \u201cscaffold\u201d control that keeps the encoding instruction but not the encoding, and they "
           "note that the same missing control exists for defences. This project carries that control over to "
           "detectors.")
    r.section("4.4 Hallucination Detection and Fact Verification")
    r.para("SelfCheckGPT detects hallucination from disagreement between sampled answers, without external evidence "
           "(Manakul et al., 2023). Semantic entropy measures uncertainty over meanings rather than tokens (Kuhn et al., "
           "2023). When evidence is available, the task becomes fact verification: FEVER pairs claims with Wikipedia "
           "evidence labelled supported, refuted or not enough information (Thorne et al., 2018), and HaluEval provides "
           "question-answering pairs with hallucinated and correct answers (Li et al., 2023). TruthfulQA measures whether "
           "models repeat common misconceptions (Lin et al., 2022). GuardShield's Stage 2 uses an NLI cross-encoder, which "
           "is a single forward pass rather than many samples, and keeps the three-way label so that \u201cnot enough "
           "evidence\u201d is not reported as a hallucination.")
    r.section("4.5 Remedies for Obfuscation")
    r.para("Two remedies exist. Canonicalization rewrites the input before the detector sees it: LLM Guard's "
           "InvisibleText scanner deletes invisible Unicode characters (Protect AI, 2024), and similar normalizers have "
           "been placed in front of a Polish safety classifier and at retrieval ingestion, reporting attack-side metrics "
           "only. Augmentation retrains the detector on perturbed text; HiveTraceGuard-Pro reports that raising recall on "
           "obfuscated attacks repeatedly raised false alarms on obfuscated benign text (Oblakov et al., 2026). Broken-Token "
           "uses the number of characters per token as an obfuscation signal, and an independent analysis found Unicode "
           "normalization inside Prompt Guard 2's tokenizer (Chester, 2025).")
    r.section("4.6 Research Gap")
    r.para("No prior work perturbs benign text exactly as it perturbs attacks when evaluating third-party "
           "prompt-injection detectors. Without that control, an evaluation cannot distinguish a detector that still "
           "recognises intent from one that blocks every unfamiliar format, nor say whether a failure can be fixed by "
           "moving the threshold. No prior work compares canonicalization and augmentation on the same detector with the "
           "benign false-positive rate measured. Table 4.1 summarises the closest work.")
    r.table(["Work", "What it does", "What this project adds"],
            [["Zhang et al. (2026)", "Benign arm and scaffold control under encodings, for chat models", "The same control for detectors, length-matched pairs, AUROC per condition"],
             ["Oblakov et al. (2026)", "Two-sided obfuscation for its own guard", "19 third-party detectors; tests the guard itself"],
             ["Shire and Kim (2026)", "Detector benchmark, attack-only obfuscation", "The benign arm; used as second data source"],
             ["Liu (2026)", "15-detector over-defense audit on clean text", "Obfuscation; opposite failure directions"],
             ["Fairoze et al. (2026)", "Encoded attacks on 14 guards", "Measures the benign-side cost"],
             ["Li et al. (2025)", "Over-defense from trigger words", "Over-defense from format"]],
            "Closest related work and the gap addressed", widths=[1.35, 2.2, 2.2])


def ch_methodology(r):
    r.chapter_heading("System Design and Methodology")
    r.section("5.1 System Architecture")
    fig = r.figure(FIG / "architecture.png", "GuardShield AI request path: each stage can stop the request or the answer")
    r.para(f"{fig} shows the request path. The client sends an OpenAI-style chat request to the proxy. Stage 1 scores the "
           "prompt; a risky prompt is rejected with HTTP 403. A safe prompt is forwarded to the upstream LLM, whose "
           "streamed tokens pass through the entropy monitor. The completed answer can be checked by Stage 2 against "
           "retrieval context. The proxy signs every assistant message it relays with HMAC-SHA256, so that a later request "
           "containing the same message can be trusted without rescanning it, while a forged \u201cassistant\u201d turn "
           "is scanned like user text.")
    r.section("5.2 Stage 1: Prompt-Injection Classifier")
    r.subsection("5.2.1 Data")
    r.para("The training corpus combines attacks from the SPML benchmark (Sharma et al., 2024), the Jayavibhav injection "
           "suite and the deepset dataset (deepset, 2023) with benign questions from TruthfulQA (Lin et al., 2022). It is "
           "split into 3,253 training, 697 validation and 698 test prompts. A separate zero-shot set of 500 prompts "
           "contains 76 human-written jailbreaks, 174 template-shifted injections and 250 benign queries that the model "
           "never saw.")
    r.subsection("5.2.2 Model and Training")
    r.para("Stage 1 fine-tunes microsoft/deberta-v3-small (He et al., 2023), which has 44.3 M backbone parameters and "
           "142.6 M parameters including its 128 k-token vocabulary. Training runs in two stages: three epochs at learning "
           "rate 2 \u00d7 10\u207b\u2075 with batch size 16 and maximum length 128, then one epoch at 1 \u00d7 10\u207b\u2075 "
           "with hard negatives (benign code, mathematics, conversational and Hinglish turns) and hard attacks. During the "
           "project audit, 29 hard-negative items were found to overlap evaluation data; they were removed and the model "
           "was retrained from scratch, and the reported numbers come from that decontaminated model.")
    r.subsection("5.2.3 Inference")
    r.para("Prompts of up to 126 tokens are scored in one pass. Longer prompts are split into windows of 126 tokens with a "
           "stride of 64, and the highest window score is used, so an attack cannot be hidden behind padding. A prompt is "
           "blocked when its risk score is at least 0.5.")
    r.section("5.3 Stage 2: Fact Verifier")
    r.para("Stage 2 uses the cross-encoder/nli-deberta-v3-small model, which reads an evidence passage and a claim "
           "together and outputs probabilities for entailment, neutral and contradiction. Long evidence is split into "
           "sentence-aligned windows that fit the 256-token input together with the claim; the claim is accepted if any "
           "window entails it. A claim is flagged as a hallucination when contradiction probability is at least 0.5, and "
           "reported as unverified when the evidence is neutral.")
    r.section("5.4 Streaming Entropy Monitor and Proxy")
    r.para("For each generated token the monitor computes the Shannon entropy H = \u2212\u03a3 p\u1d62 log\u2082 p\u1d62 over the "
           "top-3 normalised probabilities, whose maximum is log\u2082 3 \u2248 1.585 bits. A token above 1.25 bits is a "
           "spike, and two consecutive spikes stop generation. The proxy is a FastAPI application that enforces a "
           "32,768-character input cap, scans each user turn both alone and with a short preceding turn as context "
           "(taking the higher risk), and strips its own signature fields before forwarding a request upstream.")
    r.section("5.5 Research Methodology: Paired Perturbation Audit (Study 1)")
    r.para(f"Study 1 asks whether a detector still separates attacks from benign text when both are obfuscated. Each of "
           f"{M['nPairs']} attacks is paired with a benign prompt of the same character length, and both members of the "
           f"pair receive the identical transformation under {M['nFamilies']} families: zero-width spaces, soft hyphens, "
           f"leetspeak, Cyrillic homoglyphs, Base64 and ROT13 wrappers with an instruction to decode, two scaffold controls "
           f"that keep the instruction around plain text, full-width characters, combining diacritics and letter spacing. "
           f"Attacks come from the Gandalf dataset (Lakera AI, 2023) and benign twins from Dolly instructions (Conover et "
           f"al., 2023); a second source repeats the study on {M['pidsPairs']} pairs from PIDS-Bench (Shire and Kim, 2026).")
    r.para("Four measurements are taken per detector and family. The within-condition AUROC between attacks and their "
           "twins measures whether the detector still ranks attacks above benign text; its status is intact, degraded "
           "or destroyed by rules fixed before the run. Attack recall, benign false-positive rate and paired joint "
           "accuracy (attack flagged and twin passed) are read at the detector's default threshold. A cell is "
           "*fail-closed* when the benign false-positive rate rises by 20 points or more, and *fail-open* when attack "
           "recall falls by 20 points or more.")
    r.para(f"The audit covers {M['nGuards']} detectors: encoder classifiers (GuardShield, ProtectAI v2, deepset, fmops, "
           "Mezzo, Horizon, Sentinel, Prompt Guard v1 and 2), generative judges (Llama Guard 3 and 4, Qwen3Guard, "
           "WildGuard, HiveTraceGuard-Pro) and a perplexity baseline. Generative judges are scored without sampling, from "
           "the probability of their unsafe verdict. Every evaluated text was also checked against the published training "
           "data of the detectors that disclose it.")
    r.section("5.6 Research Methodology: Mitigation Study (Study 2)")
    r.para("Study 2 compares two remedies on GuardShield, retrained five times per arm with different random seeds: a "
           "naive canonicalizer (NFKC and deletion of all Unicode format characters), a script-aware canonicalizer (which "
           "also folds homoglyphs, collapses letter spacing and decodes Base64 and ROT13 spans, but keeps the joiners "
           "Devanagari spelling needs), decoding alone, benign-twin augmentation (a perturbed copy of each training "
           "example for six seen families) and canonicalization plus augmentation. The shipped ProtectAI v2 model "
           "receives the inference-time arms. Each model is read at the threshold that catches 90% of its clean attacks, "
           "and families never used in training are reported separately.")


def ch_results(r):
    r.chapter_heading("Results and Analysis")
    m1, m2, m3 = R1["metrics"], R2["metrics"], R3["metrics"]
    r.section("6.1 Stage 1 Detection Performance")
    r.table(["Split", "N", "Accuracy", "Precision", "Recall", "F1", "FPR", "Median latency"],
            [["In-distribution test", "698", pct(m1["accuracy"]), pct(m1["precision"]), pct(m1["recall"]), f"{m1['f1_score']:.4f}", pct(m1["fpr"]), f"{m1['latency_p50_ms']:.2f} ms"],
             ["Zero-shot OOD", "500", pct(m2["accuracy"]), pct(m2["precision"]), pct(m2["recall"]), f"{m2['f1_score']:.4f}", pct(m2["fpr"]), f"{m2['latency_p50_ms']:.2f} ms"]],
            "Stage 1 results (decontaminated model, weights cd1e81a29c1eb942)", widths=[1.35, 0.4, 0.7, 0.7, 0.65, 0.6, 0.55, 0.8], size=9)
    fig_a = r.figure(FIG / "cm_stage1_in_dist.png", "Confusion matrix, Stage 1 in-distribution test", width=3.4)
    fig_b = r.figure(FIG / "cm_stage1_ood.png", "Confusion matrix, Stage 1 zero-shot out-of-distribution test", width=3.4)
    c1, c2 = cm(R1), cm(R2)
    r.para(f"On the in-distribution test the classifier misses {c1['fn']} of {c1['fn'] + c1['tp']} attacks and blocks "
           f"{c1['fp']} of {c1['fp'] + c1['tn']} benign prompts ({fig_a}). On unseen prompts it misses {c2['fn']} of "
           f"{c2['fn'] + c2['tp']} attacks and blocks {c2['fp']} of {c2['fp'] + c2['tn']} benign prompts ({fig_b}). Section "
           f"6.6 shows that these clean-text numbers hide a large weakness under obfuscation, and Section 6.8 that part of "
           f"the in-distribution advantage reflects overlap between SPML training text and public attack sets.")
    r.section("6.2 Comparison with Baselines")
    pi, po, ti, to = PAI["in_distribution"], PAI["out_of_distribution"], TF["in_distribution"], TF["out_of_distribution"]
    r.table(["Model", "Parameters", "In-dist. accuracy", "In-dist. recall", "OOD accuracy", "OOD recall", "Latency"],
            [["TF-IDF + logistic regression", "linear", pct(ti["accuracy"]), pct(ti["recall"]), pct(to["accuracy"]), pct(to["recall"]), "< 1 ms"],
             ["ProtectAI DeBERTa-v3-base", PAI["metadata"]["total_parameters"], pct(pi["accuracy"]), pct(pi["recall"]), pct(po["accuracy"]), pct(po["recall"]), f"{pi['latency_p50_ms']:.2f} ms"],
             ["GuardShield DeBERTa-v3-small", "142.6M", pct(m1["accuracy"]), pct(m1["recall"]), pct(m2["accuracy"]), pct(m2["recall"]), f"{m1['latency_p50_ms']:.2f} ms"]],
            "Stage 1 compared with baselines on identical splits", widths=[1.7, 0.75, 0.75, 0.7, 0.7, 0.65, 0.6], size=9)
    r.para(f"GuardShield is smaller and faster than ProtectAI's model and generalises better to the zero-shot set "
           f"({pct(m2['recall'])} against {pct(po['recall'])} recall). The TF-IDF baseline, which matches surface words, "
           f"drops to {pct(to['recall'])} recall on unseen attack templates, which shows why a contextual model is needed. "
           f"ProtectAI was not trained on these splits, so the in-distribution comparison favours GuardShield.")
    r.section("6.3 Stage 2 Fact Verification")
    pb = R3["per_source_breakdown"]
    fe, he = pb["FEVER (NAACL 2018)"], pb["HaluEval (EMNLP 2023)"]
    r.table(["Benchmark", "N", "Accuracy", "Recall (contradiction)", "Precision", "FPR", "AUROC"],
            [["FEVER", "400", pct(fe["accuracy"]), pct(fe["recall"]), pct(fe["precision"]), pct(fe["fpr"]), f"{fe['auroc']:.4f}"],
             ["HaluEval QA", "400", pct(he["accuracy"]), pct(he["recall"]), pct(he["precision"]), pct(he["fpr"]), f"{he['auroc']:.4f}"],
             ["Combined", "800", pct(m3["accuracy"]), pct(m3["recall"]), pct(m3["precision"]), pct(m3["fpr"]), f"{m3['auroc']:.4f}"]],
            "Stage 2 results on public fact-verification benchmarks", widths=[1.2, 0.45, 0.8, 1.2, 0.8, 0.6, 0.7], size=9)
    fig_c = r.figure(FIG / "cm_stage2.png", "Confusion matrix, Stage 2 on FEVER and HaluEval", width=3.4)
    tw = R3["three_way_distribution"]
    r.para(f"The verifier is strong on FEVER (AUROC {fe['auroc']:.3f}), whose claims are short and checked against a "
           f"single passage, and weak on HaluEval (AUROC {he['auroc']:.3f}), whose hallucinated answers are often "
           f"plausible elaborations that the evidence neither confirms nor refutes ({fig_c}). Of the 400 hallucinated "
           f"items, {tw['hallucination']['neutral']} are judged neutral rather than contradicted; the system reports these "
           f"as unverified instead of hiding the uncertainty.")
    r.section("6.4 Latency and Multi-Turn Behaviour")
    e = R4["metrics"]
    r.para(f"Over five repeats of 100 sequential requests on the laptop GPU, Stage 1 alone takes a median "
           f"{e['stage1_isolated']['latency_p50_ms']:.2f} ms, Stage 2 alone {e['stage2_isolated']['latency_p50_ms']:.2f} ms, "
           f"and the full pipeline {e['latency_p50_ms']:.2f} ms (interquartile range {e['latency_iqr_ms']:.2f} ms, 95th "
           f"percentile {e['latency_p95_ms']:.2f} ms).")
    g, p = MT["guardshield_eval"], MT["protectai_eval"]
    r.table(["Configuration", "User turns flagged (of 60)", "Conversations blocked (of 20)"],
            [["ProtectAI v2, each turn alone", f"{p['user_turns_false_positives']} ({pct(p['user_turns_fpr'])})", f"{p['conversations_blocked']} ({pct(p['conversation_fpr'])})"],
             ["GuardShield, unsigned history", f"{g['user_turns_false_positives']} ({pct(g['user_turns_fpr'])})", f"{g['raw_conversations_blocked']} ({pct(g['raw_conversation_fpr'])})"],
             ["GuardShield, signed assistant history", f"{g['signed_history_user_turns_false_positives']} ({pct(g['signed_history_user_turns_fpr'])})", f"{round(g['signed_history_conversation_fpr'] * 20)} ({pct(g['signed_history_conversation_fpr'])})"]],
            "False alarms on 20 benign multi-turn conversations (100 turns)", widths=[2.4, 1.7, 1.65])
    r.para("All 20 conversations are benign, so every flag is a false alarm. Signing the assistant turns that the proxy "
           "itself relayed removes them from scanning and lowers the share of blocked conversations.")
    r.section("6.5 Study 1: Failure Map of 19 Detectors")
    fig_m = r.figure(PFIG / "fig_failure_map.png", "Failure mode (fill) and within-condition AUROC (number) for every detector and perturbation family; hatching marks a destroyed signal. Gandalf \u00d7 Dolly, 500 pairs.", width=5.8)
    r.para(f"{fig_m} is the central result. The intent signal is destroyed in {M['nSigDestroyed']} of {M['nCells']} "
           f"detector\u2013family cells ({M['pctSigDestroyed']}%) and intact in only {M['nSigIntact']}. Base64 and ROT13 "
           f"wrappers destroy it in {M['nWrapDestroyed']} of {M['nWrapCells']} cells, while the scaffold control, which "
           f"keeps the decoding instruction around plain text, leaves it intact in {M['nScaffoldIntact']} of "
           f"{M['nScaffoldCells']}; the encoding, not the wording, removes the signal.")
    r.para(f"Attack-only evaluation hides the problem. Of the {M['nAttackRobust']} cells whose attack recall stays within "
           f"5 points of clean text, {M['nAttackRobustFC']} ({M['pctAttackRobustFC']}%) are fail-closed: the detector keeps "
           f"its recall only because it now also blocks the benign twin. For example, ProtectAI v2 catches "
           f"{M['protectaiBsfTPR']}% of Base64-wrapped attacks and blocks {M['protectaiBsfFPR']}% of Base64-wrapped benign "
           f"prompts. Conversely, Prompt Guard 2 86M falls from {M['pgTwoEightSixCleanTPR']}% recall on clean text to "
           f"{M['pgTwoEightSixShyTPR']}% under soft hyphens while its false-positive rate stays at "
           f"{M['pgTwoEightSixShyFPR']}%, a failure that a benign-only audit would score as perfect.")
    r.para(f"The direction of failure belongs to a detector\u2013family combination, not to a detector: {M['nMixedGuards']} "
           f"detectors fail closed under some families and open under others. HiveTraceGuard-Pro, the only public detector "
           f"trained on obfuscated text of both labels, is near-perfect on clean text (AUROC {M['htCleanAUC']}) yet loses "
           f"the signal in {M['htDestroyed']} of {M['nFamilies']} families. Ranking detectors by perturbed-attack recall "
           f"and by paired accuracy gives unrelated orders (Kendall \u03c4 = {M['hTwoTau']}), so attack-only leaderboards do "
           f"not predict real robustness.")
    r.para(f"On the second source (PIDS-Bench), every one of the {M['replDirCells']} cells with a clear failure direction "
           f"keeps it, and the failure mode matches in {M['replModeSame']} of {M['replModeCells']} cells. Appendix B shows "
           f"the second failure map.")
    r.section("6.6 Why Detectors Fail: the Tokenizer")
    r.table(["Tokenizer outcome", "Intact", "Degraded", "Destroyed"],
            [["Perturbation normalized away", M["mechObfNormalizedIntact"], M["mechObfNormalizedDegraded"], M["mechObfNormalizedDestroyed"]],
             ["Collapsed into unknown tokens", M["mechObfUnknownIntact"], M["mechObfUnknownDegraded"], M["mechObfUnknownDestroyed"]],
             ["Fragmented into more tokens", M["mechObfFragmentedIntact"], M["mechObfFragmentedDegraded"], M["mechObfFragmentedDestroyed"]]],
            "Signal status of character-family cells by what the detector's tokenizer does (Gandalf \u00d7 Dolly)", widths=[2.6, 1.0, 1.0, 1.15])
    r.para(f"When the tokenizer maps the perturbed text back to the clean token sequence, the signal survives in all "
           f"{M['mechObfNormalized']} cases; this explains why Prompt Guard 2 ignores zero-width characters, full-width "
           f"forms and letter spacing. When words become unknown tokens, the signal is destroyed in all {M['mechObfUnknown']} "
           f"cases. When the text fragments, encoder classifiers keep the signal in only {M['mechObfFragEncIntact']} of "
           f"{M['mechObfFragEnc']} cells, whereas the larger generative judges sometimes read through it. Once a detector "
           f"cannot read its input it returns its usual verdict: {M['mechObfDirPct']}% of destroyed cells fail in that "
           f"detector's majority direction.")
    r.section("6.7 Study 2: Canonicalization versus Augmentation")
    rows = []
    for arm, label in (("None", "None (retrained)"), ("Naive", "Naive canonicalizer"), ("ScriptAware", "Script-aware canonicalizer"),
                       ("ScriptReplace", "Script-aware + decode-and-replace"), ("Augment", "Benign-twin augmentation"),
                       ("CanonAugment", "Canonicalize + augment")):
        k = f"scPids{arm}"
        rows.append([label, M[f"{k}SeenCharAuc"], M[f"{k}SeenWrapperAuc"], M[f"{k}HeldOutAuc"], M[f"{k}SeenCharFpr"] + "%", M[f"{k}SeenWrapperFpr"] + "%"])
    r.table(["Arm (GuardShield, 5 seeds)", "AUROC seen char.", "AUROC wrappers", "AUROC held out", "FPR seen char.", "FPR wrappers"],
            rows, "Study 2 on PIDS-Bench, means over five seeds; FPR at the threshold that catches 90% of clean attacks",
            widths=[2.0, 0.75, 0.75, 0.75, 0.75, 0.75], size=9)
    r.para(f"Script-aware canonicalization restores most of the signal on seen character families (AUROC "
           f"{M['scPidsNoneSeenCharAuc']} to {M['scPidsScriptAwareSeenCharAuc']}) and halves the benign false-positive rate "
           f"at matched recall, while augmentation reaches only {M['scPidsAugmentSeenCharAuc']}. On the Gandalf pairs the "
           f"two tie ({M['scObfAugmentSeenCharAuc']} against {M['scObfScriptAwareSeenCharAuc']}), also after removing the "
           f"{M['scObfDeconExcluded']} pairs that overlap GuardShield's training data, so augmentation helps on familiar "
           f"data and fails to transfer to a new source. The held-out advantage of canonicalization comes from its "
           f"letter-spacing rule; diacritics, which no rule covers, defeat both arms.")
    fig_k = r.figure(PFIG / "fig_coupling.png", "Benign-twin augmentation over training mixtures: recall and false-positive rate fall together", width=5.6)
    r.para(f"Decoding restores the wrapper signal but, under the rule of keeping the higher of the raw and decoded scores, "
           f"leaves the benign false-positive rate at {M['scPidsRescanOnlySeenWrapperFpr']}%; replacing the encoded input with "
           f"its decoding lowers it to {M['scPidsScriptReplaceSeenWrapperFpr']}%. {fig_k} shows that augmentation lowers "
           f"default-threshold recall from {M['scPidsNoneSeenCharTprDefault']}% to {M['scPidsAugmentSeenCharTprDefault']}% "
           f"together with the false-positive rate ({M['scPidsNoneSeenCharFprDefault']}% to "
           f"{M['scPidsAugmentSeenCharFprDefault']}%), the same coupling HiveTraceGuard-Pro reported for its own model. In "
           f"{M['ayaTexts']} native-written Hindi prompts from the Aya Dataset (Singh et al., 2024), only "
           f"{M['ayaTextsJoiner']} contains a joiner that the naive canonicalizer would delete.")
    r.section("6.8 Training-Data Contamination")
    r.para(f"Checking the evaluation texts against the published training data of {M['nAuditGuards']} detectors showed "
           f"three overlaps: Horizon guard-base trained on Gandalf's training split ({M['horizonContamAttacks']} of 500 "
           f"attacks), GuardShield's SPML training rows contain {M['gsContamAttacks']} of the Gandalf attacks, and ProtectAI "
           f"v2's listed training data include most Dolly prompts. Removing each detector's contaminated pairs changes no "
           f"failure mode, and no audited corpus contains any PIDS-Bench text. Overlap inflates clean-text results but does "
           f"not explain the failure map.")


def ch_management(r):
    r.chapter_heading("Project Management Approach")
    r.section("7.1 Project Timeline")
    fig = r.figure(FIG / "gantt.png", "Project schedule over the 12-week NTCC period", width=5.8)
    r.para(f"{fig} shows the schedule followed, as recorded in the weekly progress reports. The NTCC calendar fixed the "
           "external milestones: commencement on 20 July 2026, the first progress review on 24\u201327 August, the second on "
           "28 September\u20131 October, the end date on 9 October and the final report on 26 October 2026.")
    r.table(["Week", "Milestone", "Deliverable"],
            [["W1", "Problem statement and architecture", "WPR 1, synopsis"],
             ["W2", "Literature survey and threat model", "WPR 2, dataset catalogue"],
             ["W3\u2013W4", "Data ingestion, obfuscation synthesis, Stage 1 training", "Train/validation/test splits, classifier"],
             ["W5\u2013W6", "Stage 2 verifier, pipeline, proxy, entropy monitor", "End-to-end proxy"],
             ["W7\u2013W8", "Multi-dataset benchmarking, baselines", "Comparison tables"],
             ["W9\u2013W10", "Mega benchmark, FEVER/HaluEval, latency, confidence intervals", "Verified results"],
             ["W10\u2013W11", "Project audit, decontaminated retraining", "Audited code and results"],
             ["W10\u2013W12", "Study 1 audit, Study 2 mitigation, research paper", "IEEE-format paper, this report"]],
            "Milestones and deliverables", widths=[0.85, 3.0, 1.9])
    r.section("7.2 Project Roles and Responsibilities")
    r.table(["Role", "Responsibilities", "Participant"],
            [["Lead architect", "Pipeline implementation, model training, benchmarking, research audit, paper", STUDENTS[0][0]],
             ["Research analyst", "Literature survey, NLI formulation, related-work positioning", STUDENTS[1][0]],
             ["Data engineer", "Multi-corpus curation, preprocessing, dataset documentation", STUDENTS[2][0]],
             ["Faculty guide", "Supervision, reviews, research direction", GUIDE]],
            "Roles and responsibilities (as recorded in the weekly progress reports)", widths=[1.3, 3.15, 1.3])
    r.para("Work was coordinated through weekly meetings with the guide, a shared Git repository with automated tests, "
           "and a written specification for the research study in which every design decision and change is dated.")


def ch_risk(r):
    r.chapter_heading("Risk Assessment")
    r.para("Table 8.1 lists the risks identified at the start of the project and during it, with the mitigation applied.")
    r.table(["Risk", "Level (L/M/H)", "Likelihood", "Mitigation strategy"],
            [["Project size exceeds 12 weeks", "H", "High", "Hindi benchmark moved to the 8th-semester project; scope frozen in a written specification"],
             ["Laptop GPU too small for large judges", "M", "High", "Large judges scored on free Kaggle T4 GPUs; scoring made resumable"],
             ["Training/evaluation data contamination", "H", "Medium", "Decontamination before training; contamination audit of 28 public corpora"],
             ["Results not reproducible", "H", "Medium", "Pinned model revisions, dataset and weight hashes, generated tables"],
             ["Gated or unavailable models, Hub outages", "M", "Medium", "Licences accepted in advance; automatic retry of transient errors"],
             ["Competing publications on the same gap", "H", "High", "Novelty check; narrowed claims; early write-up"],
             ["Similarity index above 15%", "M", "Low", "Report written in the team's own words; sources cited"],
             ["Detector misconfiguration giving wrong scores", "H", "Medium", "Each generative judge checked against its own generated verdicts before scoring"]],
            "Project risk assessment", widths=[1.65, 0.75, 0.75, 2.6], size=9.5)


def ch_limitations(r):
    r.chapter_heading("Limitations and Future Scope")
    r.section("9.1 Limitations")
    r.bullets([
        "Stage 2 is weak on HaluEval-style answers, which are often plausible but unsupported rather than contradicted.",
        "Stage 1's clean-text accuracy partly reflects overlap between its SPML training data and public attack sets; under obfuscation it fails closed like other fine-tuned classifiers.",
        "The audit uses fixed, non-adaptive perturbations; an attacker who adapts to a specific detector would do at least as well.",
        "Gandalf attacks mostly target password extraction, and PIDS-Bench is dominated by templated injections, so other attack styles may behave differently.",
        "The canonicalizer has no rule for leetspeak or diacritics, and collapsing letter spacing cannot always recover word boundaries.",
        "Retraining was limited to the small DeBERTa backbone with five seeds because of the 4 GB GPU.",
    ])
    r.section("9.2 Future Scope")
    r.bullets([
        "A native-speaker Hindi, romanized Hindi and Hinglish benchmark measuring detector false positives per script (8th-semester project).",
        "Adding script-aware canonicalization with decode-and-replace to the GuardShield proxy as a default pre-processing step.",
        "Training Stage 1 on paired, two-sided obfuscated data and testing it on families held out from training.",
        "Improving Stage 2 with retrieval of several evidence passages and calibration on HaluEval-style answers.",
        "Adaptive attacks against the full pipeline, and deployment tests with real agent tool outputs.",
    ])


def ch_conclusion(r):
    r.chapter_heading("Conclusion")
    r.para(f"GuardShield AI meets its engineering goals: an open sidecar proxy that blocks prompt injections at a median of "
           f"{R1['metrics']['latency_p50_ms']:.1f} ms with a {pct(R1['metrics']['fpr'])} false-positive rate on held-out "
           f"prompts, checks answers against evidence, and adds {R4['metrics']['latency_p50_ms']:.1f} ms per request in "
           f"total on a laptop GPU, with every number reproducible from committed files.")
    r.para(f"The research part of the project shows that such numbers are not enough. When benign text is perturbed "
           f"exactly like attacks, {M['nGuards']} detectors, including GuardShield, lose the ability to separate the two in "
           f"most cells, and attack-only evaluation mistakes over-blocking for robustness. The failure follows from what "
           f"each tokenizer does to the perturbed text, and fixing the input with a script-aware canonicalizer helps more, "
           f"and more reliably across data sources, than retraining on perturbed examples. These findings are written up "
           f"as a research paper, and they define the next step for the project: a canonicalizing, multilingual GuardShield "
           f"evaluated with paired benign controls.")


def ch_contribution(r):
    r.chapter_heading("Individual Contribution")
    r.para("[To be completed and confirmed by each team member. The entries below follow the roles recorded in the "
           "weekly progress reports.]", italic=True)
    for (name, enr), text in zip(STUDENTS, (
            "Lead architect. Implemented the Stage 1 classifier, the Stage 2 verifier, the streaming entropy monitor and the "
            "FastAPI proxy; trained and evaluated the models; ran the research audit on Kaggle and the mitigation study; "
            "prepared the research paper.",
            "Research analyst. Carried out the literature survey and the formulation of NLI-based fact verification; "
            "prepared the related-work positioning and the progress presentations.",
            "Data engineer. Curated and preprocessed the multi-source datasets, built the train, validation, test and "
            "out-of-distribution splits, and documented dataset provenance and licences.")):
        r.subsection(f"{name} ({enr})")
        r.para(text)


# =================================================================== back matter
REFERENCES = [
    "Chester, A. (2025). Tokenization confusion. XPN InfoSec Blog. https://blog.xpnsec.com/tokenization-confusion/",
    "Conover, M., Hayes, M., Mathur, A., Xie, J., Wan, J., Shah, S., Ghodsi, A., Wendell, P., Zaharia, M. and Xin, R. (2023). Free Dolly: Introducing the world's first truly open instruction-tuned LLM. Databricks blog.",
    "deepset (2023). prompt-injections [Dataset]. Hugging Face. https://huggingface.co/datasets/deepset/prompt-injections",
    "Fairoze, J., Garg, S., Lee, K. and Wang, M. (2026). Bypassing prompt guards in production with controlled-release prompting. In USENIX Security Symposium. arXiv:2510.01529.",
    "Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T. and Fritz, M. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security.",
    "Hackett, W., Birch, L., Trawicki, S., Suri, N. and Garraghan, P. (2025). Bypassing LLM guardrails: An empirical analysis of evasion attacks against prompt injection and jailbreak detection systems. In Proceedings of the First Workshop on LLM Security (LLMSEC). arXiv:2504.11168.",
    "Han, S., Rao, K., Ettinger, A., Jiang, L., Lin, B. Y., Lambert, N., Choi, Y. and Dziri, N. (2024). WildGuard: Open one-stop moderation tools for safety risks, jailbreaks, and refusals of LLMs. In Advances in Neural Information Processing Systems (Datasets and Benchmarks Track).",
    "He, P., Gao, J. and Chen, W. (2023). DeBERTaV3: Improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing. In International Conference on Learning Representations.",
    "Inan, H., Upasani, K., Chi, J., Rungta, R., Iyer, K., Mao, Y., Tontchev, M., Hu, Q., Fuller, B., Testuggine, D. and Khabsa, M. (2023). Llama Guard: LLM-based input-output safeguard for human-AI conversations. arXiv:2312.06674.",
    "Kuhn, L., Gal, Y. and Farquhar, S. (2023). Semantic uncertainty: Linguistic invariances for uncertainty estimation in natural language generation. In International Conference on Learning Representations. arXiv:2302.09664.",
    "Lakera AI (2023). gandalf_ignore_instructions [Dataset]. Hugging Face. https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions",
    "Li, H., Liu, X., Zhang, N. and Xiao, C. (2025). PIGuard: Prompt injection guardrail via mitigating overdefense for free. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics, pp. 30420\u201330437.",
    "Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y. and Wen, J.-R. (2023). HaluEval: A large-scale hallucination evaluation benchmark for large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. arXiv:2305.11747.",
    "Lin, S., Hilton, J. and Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics. arXiv:2109.07958.",
    "Liu, Z. (2026). Passing the test you trained on: Re-evaluating prompt-injection detectors for LLM agents. arXiv:2610.03448.",
    "Manakul, P., Liusie, A. and Gales, M. J. F. (2023). SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing. arXiv:2303.08896.",
    "Meta (2025). Llama Prompt Guard 2 model card. https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M",
    "Oblakov, N., Sadiekh, S. and Kokuykin, E. (2026). HiveTraceGuard-Pro: A compact generative guardrail for prompt injection, jailbreaks, and adversarial obfuscation. arXiv:2609.01046.",
    "Perez, F. and Ribeiro, I. (2022). Ignore previous prompt: Attack techniques for language models. arXiv:2211.09527.",
    "Protect AI (2024). LLM Guard: InvisibleText scanner. https://github.com/protectai/llm-guard",
    "Sharma, R. K., Gupta, V. and Grossman, D. (2024). SPML: A DSL for defending language models against prompt attacks. arXiv:2402.11755.",
    "Shire, Y. K. and Kim, S.-C. (2026). PIDS-Bench: Evaluating prompt-injection detectors under over-defense, obfuscation, and distribution shift. IEEE Access, 14, pp. 134184\u2013134205.",
    "Singh, S., Vargus, F., Dsouza, D., Karlsson, B. F. et al. (2024). Aya Dataset: An open-access collection for multilingual instruction tuning. arXiv:2402.06619.",
    "Thorne, J., Vlachos, A., Christodoulopoulos, C. and Mittal, A. (2018). FEVER: A large-scale dataset for fact extraction and VERification. In Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics. arXiv:1803.05355.",
    "Zhang, H., Xu, H., Luo, X., Liu, H., Chen, Y., Xiao, Z., Feng, Y., Guan, X., Zandsalimy, M. and Sushmita, S. (2026). Refusing everything looks safe: Restoring the benign arm to encoded-prompt evaluation. arXiv:2609.26176.",
    "Zhao, H., Yuan, C., Huang, F., Hu, X., Zhang, Y., Yang, A. et al. (2025). Qwen3Guard technical report. arXiv:2510.14276.",
]


def references(r):
    r.page_break()
    r.heading("REFERENCES", 1)
    for ref in sorted(REFERENCES, key=lambda s: s.lower()):
        p = r.doc.add_paragraph(ref, style="Reference")
        p.paragraph_format.space_after = Pt(6)


def appendices(r):
    r.appendix_heading("A", "Research Paper")
    r.para("The research outcome of the project is the paper \u201cGuards That Reject the Unfamiliar: Format-Triggered "
           f"Over-Defense in Prompt-Injection Detectors\u201d by {', '.join(n for n, _ in STUDENTS)} and {GUIDE.replace('Dr. ', '')}, "
           "prepared in the IEEE conference format (repository file paper1/paper/main.tex). It reports Study 1, the "
           "tokenizer analysis and Study 2 of this report. [Update with the venue and the submission or publication "
           "evidence once available, as required by the NTCC guidelines.]")
    r.appendix_heading("B", "Second Failure Map (PIDS-Bench)")
    r.figure(PFIG / "fig_failure_map_pids.png", "Study 1 repeated on 200 PIDS-Bench pairs; encoding as in the main failure map", width=5.8)
    r.appendix_heading("C", "Reproducing the Results")
    r.para("All code, configurations and result files are in the project repository. The main commands are:")
    r.bullets([
        "python src/train_prescan_v3.py and python scripts/train_stage1_hard_negatives.py: train Stage 1.",
        "python src/evaluate_full_suite_v3.py: evaluate Stage 1 and Stage 2 and write docs/01 Reports/raw_eval_*.json.",
        "python src/proxy_server.py: run the sidecar proxy on port 8000.",
        "python -m guard_audit.run_audit build | score | metrics | report: the Study 1 audit harness.",
        "python paper1/study_c/run_study_c.py train | guards | score | metrics: the Study 2 pipeline.",
        "python paper1/paper/make_assets.py: regenerate every number, table and figure of the paper.",
        "python -m pytest tests/: the automated test suite (40 tests).",
    ])
    r.appendix_heading("D", "Weekly Progress Reports")
    r.para("Weekly progress reports for weeks 1 to 12 are kept in the repository folder docs/02 Weekly WPRs and were "
           "submitted on Amizone as required. [Attach the signed copies and the minor project diary when binding.]")


def main():
    r = Report()
    title_page(r)
    r.new_section("lowerRoman", 2, "footer_center")
    declaration(r)
    certificate(r)
    acknowledgement(r)
    contents_pages(r)
    abstract(r)
    r.new_section("decimal", 1, "header_right")
    for ch in (ch_introduction, ch_scope, ch_requirements, ch_literature, ch_methodology, ch_results, ch_management,
               ch_risk, ch_limitations, ch_conclusion, ch_contribution):
        ch(r)
    references(r)
    appendices(r)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / "GuardShield AI - Final Project Report.docx"
    r.save(out)
    print("wrote", out)
    return out


if __name__ == "__main__":
    main()
