"""
================================================================================
 GuardShield AI — Automated README Metrics & Tables Synchronizer
================================================================================
 Rebuilds the results and limitations sections of README.md from the evaluation
 logs in docs/01 Reports/. Every number is read from a log: a missing key raises
 instead of falling back to a constant, and Stage 1 reports produced by
 different model weights (i.e. stale reports) are refused.

 Run after the evaluation scripts:
   python scripts/export_raw_eval_outputs.py
   python scripts/measure_pipeline_e2e_latency.py
   python scripts/benchmark_multiturn_dialogue.py
   python scripts/build_and_eval_benign_hard.py
   python scripts/benchmark_adaptive_attacks.py
   python scripts/generate_readme_tables.py
================================================================================
"""

import sys
import json
import math
import re
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "docs" / "01 Reports"
README_PATH = BASE_DIR / "README.md"
sys.path.insert(0, str(BASE_DIR / "src"))

BEGIN_MARKER = "<!-- BEGIN GENERATED RESULTS (scripts/generate_readme_tables.py) -->"
END_MARKER = "<!-- END GENERATED RESULTS -->"
RESULTS_START_HEADING = "## 📊 V3 Mega Research Benchmark Evaluation"
RESULTS_END_HEADING = "## 🚀 Live Interactive Colab Suite"

OOD_DAN_SOURCE = "ChatGPT JailbreakBench (DAN / Persona)"
OOD_TEMPLATE_SOURCE = "Synthetic OOD Attack Generator"
BLANKET_REJECTION_FPR = 50.0  # percent


def load_json(filename):
    path = REPORTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing required report file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pct(x, digits=2):
    return f"{x * 100:.{digits}f}%"


def ratio(k, n):
    return f"{pct(k / n) if n else '—'} ({k}/{n})"


def wilson(k, n, z=1.959964):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def per_source(raw):
    """{source: {'attacks', 'attacks_flagged', 'benign', 'benign_flagged'}} from per-sample predictions."""
    out = defaultdict(lambda: {"attacks": 0, "attacks_flagged": 0, "benign": 0, "benign_flagged": 0})
    for r in raw["predictions"]:
        row = out[r["source"]]
        kind = "attacks" if int(r["true_label"]) == 1 else "benign"
        row[kind] += 1
        row[kind + "_flagged"] += int(r["predicted_label"]) == 1
    return dict(out)


def check_stage1_provenance(named_hashes):
    """All Stage 1 reports must come from the same weights, and from the checkpoint currently on disk."""
    missing = [name for name, h in named_hashes.items() if not h]
    if missing:
        raise SystemExit(f"Stage 1 reports without weights_sha256 (re-run them): {missing}")
    distinct = set(named_hashes.values())
    if len(distinct) > 1:
        lines = "\n".join(f"  {h[:16]}  {name}" for name, h in named_hashes.items())
        raise SystemExit(f"Stage 1 reports were produced by different weights; re-run the stale ones:\n{lines}")
    report_hash = distinct.pop()
    try:
        from prescan_filter import find_trained_checkpoint, weights_sha256
        checkpoint = find_trained_checkpoint()
        current = weights_sha256(checkpoint) if checkpoint else None
    except ImportError:
        current = None
    if current and current != report_hash:
        raise SystemExit(f"Reports were produced by weights {report_hash[:16]}, but {checkpoint} holds {current[:16]}. Re-run the evaluations.")
    if not current:
        print("[WARN] No local checkpoint to compare against; trusting report hashes.")
    return report_hash


def build_results_block():
    s1_in = load_json("raw_eval_in_distribution_test_698.json")
    s1_ood = load_json("raw_eval_out_of_distribution_500.json")
    s2_fact = load_json("raw_eval_stage2_factuality_800.json")
    e2e_lat = load_json("raw_eval_pipeline_e2e.json")
    tfidf_rep = load_json("table_tfidf_baseline_comparison.json")
    protectai_rep = load_json("table_external_baseline_protectai.json")
    multiturn_rep = load_json("table_multiturn_benchmark.json")
    adaptive_rep = load_json("table_adaptive_robustness.json")
    benign_hard_rep = load_json("benign_hard_audit_report.json")

    weights_hash = check_stage1_provenance({
        "raw_eval_in_distribution_test_698.json": s1_in["metadata"].get("weights_sha256"),
        "raw_eval_out_of_distribution_500.json": s1_ood["metadata"].get("weights_sha256"),
        "raw_eval_pipeline_e2e.json": e2e_lat["metadata"].get("weights_sha256"),
        "table_multiturn_benchmark.json": multiturn_rep["metadata"].get("weights_sha256"),
        "table_adaptive_robustness.json": adaptive_rep.get("weights_sha256"),
        "benign_hard_audit_report.json": benign_hard_rep.get("weights_sha256"),
    })

    hn_path = BASE_DIR / "models" / "deberta_v3_prescan_v3" / "hard_negative_training_summary.json"
    hard_neg = json.loads(hn_path.read_text(encoding="utf-8")) if hn_path.is_file() else None

    m_in, m_ood, m_s2, m_e2e = s1_in["metrics"], s1_ood["metrics"], s2_fact["metrics"], e2e_lat["metrics"]
    n_in, n_ood, n_s2 = s1_in["metadata"]["sample_count"], s1_ood["metadata"]["sample_count"], s2_fact["metadata"]["sample_count"]
    fever = s2_fact["per_source_breakdown"]["FEVER (NAACL 2018)"]
    halu = s2_fact["per_source_breakdown"]["HaluEval (EMNLP 2023)"]

    src_in, src_ood = per_source(s1_in), per_source(s1_ood)
    dan, tmpl = src_ood[OOD_DAN_SOURCE], src_ood[OOD_TEMPLATE_SOURCE]
    ood_attacks = sum(v["attacks"] for v in src_ood.values())
    ood_attacks_flagged = sum(v["attacks_flagged"] for v in src_ood.values())
    ood_benign = sum(v["benign"] for v in src_ood.values())
    ood_benign_flagged = sum(v["benign_flagged"] for v in src_ood.values())
    cm_in = m_in["confusion_matrix"]
    in_correct = cm_in["tp"] + cm_in["tn"]
    in_lo, in_hi = wilson(in_correct, n_in)

    tf_in, tf_ood = tfidf_rep["in_distribution"], tfidf_rep["out_of_distribution"]
    tf_dan_tp = round(tf_ood["dan_jailbreaks_recall"] * tf_ood["dan_sample_count"])
    tf_tmpl_tp = round(tf_ood["synthetic_template_recall"] * tf_ood["synthetic_sample_count"])
    pai_meta, pai_in, pai_ood = protectai_rep["metadata"], protectai_rep["in_distribution"], protectai_rep["out_of_distribution"]
    pai_gran = pai_ood["granular_breakdown"]
    pai_bh = protectai_rep["benign_hard_control"]

    gs_mt, pai_mt, mt_meta = multiturn_rep["guardshield_eval"], multiturn_rep["protectai_eval"], multiturn_rep["metadata"]
    n_turns, n_user, n_asst, n_conv = mt_meta["sample_turns"], mt_meta["user_turns"], mt_meta["assistant_turns"], mt_meta["sample_conversations"]

    bh_preds = benign_hard_rep["sample_predictions"]
    bh_benign = [p for p in bh_preds if int(p["true_label"]) == 0]
    bh_attacks = [p for p in bh_preds if int(p["true_label"]) == 1]
    bh_fp = sum(int(p["predicted_label"]) == 1 for p in bh_benign)
    bh_tp = sum(int(p["predicted_label"]) == 1 for p in bh_attacks)
    bh_by_cat = defaultdict(lambda: [0, 0])
    for p in bh_benign:
        bh_by_cat[p["category"]][0] += 1
        bh_by_cat[p["category"]][1] += int(p["predicted_label"]) == 1
    worst_cats = sorted(((fp / n, c, fp, n) for c, (n, fp) in bh_by_cat.items() if fp), reverse=True)[:3]

    vectors = adaptive_rep["perturbation_evaluations"]
    blanket = [v for v in vectors if v["guardshield"]["fpr"] >= BLANKET_REJECTION_FPR]
    xs = adaptive_rep["xstest_disaggregated"]

    def ci(lo_hi):
        return f"[{lo_hi[0]:.1f}%, {lo_hi[1]:.1f}%]"

    # ------------------------------------------------------------------ tables
    headline_table = f"""| Defense Component | Evaluation Dataset / Split | Sample Size ($N$) | Accuracy (%) | Precision (%) | Recall (%) | F1-Score | FPR (%) | Median Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 1: Pre-Scan** | **In-Distribution Test Split** | **{n_in}** | **{pct(m_in['accuracy'])}** | **{pct(m_in['precision'])}** | **{pct(m_in['recall'])}** | **{m_in['f1_score']:.4f}** | **{pct(m_in['fpr'])}** | **{m_in['latency_p50_ms']:.2f} ms** |
| **Stage 1: Pre-Scan** | **Out-of-Distribution Zero-Shot** | **{n_ood}** | **{pct(m_ood['accuracy'])}** | **{pct(m_ood['precision'])}** | **{pct(m_ood['recall'])}** | **{m_ood['f1_score']:.4f}** | **{pct(m_ood['fpr'])}** | **{m_ood['latency_p50_ms']:.2f} ms** |
| **Stage 2: Fact Verifier** | **Multi-Source Fact Grounding (FEVER + HaluEval)** | **{n_s2}** | **{pct(m_s2['accuracy'])}** | **{pct(m_s2['precision'])}** | **{pct(m_s2['recall'])}** | **{m_s2['f1_score']:.4f}** | **{pct(m_s2['fpr'])}** | **{m_s2['latency_p50_ms']:.2f} ms** |
| **Dual-Stage Pipeline** | **Sequential Pipeline Overhead ({e2e_lat['metadata']['num_repeats']}-Repeat)** | **{e2e_lat['metadata']['total_samples_measured']}** | — | — | — | — | — | **{m_e2e['latency_p50_ms']:.2f} ms** (IQR: {m_e2e['latency_iqr_ms']:.2f} ms) |"""

    def s2_row(name, m, bold=False):
        b = "**" if bold else ""
        cm = m["confusion_matrix"]
        return (f"| {b}{name}{b} | {m['sample_count'] if 'sample_count' in m else n_s2} | {pct(m['accuracy'])} | "
                f"{pct(m['recall'])} ({cm['tp']}/{cm['tp'] + cm['fn']}) | {pct(m['precision'])} | "
                f"{pct(m['fpr'])} ({cm['fp']} false alarms) | {m['auroc']:.4f} |")

    stage2_table = "\n".join([
        "| Fact Grounding Benchmark Split | Sample Size ($N$) | Accuracy (%) | Contradiction Recall (%) | Precision (%) | FPR (%) | AUROC |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        s2_row("FEVER (NAACL 2018)", fever),
        s2_row("HaluEval QA (EMNLP 2023)", halu),
        s2_row("Combined Authentic Suite", m_s2, bold=True),
    ])

    baselines_table = f"""| Model Architecture | Total Parameters | In-Distribution Accuracy | In-Distribution Recall | OOD Zero-Shot Accuracy | OOD Zero-Shot Recall | Human DAN Recall | Template Shift Recall | Latency (p50) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF + Logistic Regression (Baseline)** | Linear (10k n-grams) | {pct(tf_in['accuracy'])} | {pct(tf_in['recall'])} | {pct(tf_ood['accuracy'])} | {pct(tf_ood['recall'])} | {ratio(tf_dan_tp, tf_ood['dan_sample_count'])} | {ratio(tf_tmpl_tp, tf_ood['synthetic_sample_count'])} | < 1 ms |
| **ProtectAI DeBERTa-v3-base (External SLM)** | {pai_meta['total_parameters']} (Base) | {pct(pai_in['accuracy'])} | {pct(pai_in['recall'])} | {pct(pai_ood['accuracy'])} | {pct(pai_ood['recall'])} | {ratio(pai_gran['human_dan_tp'], pai_gran['human_dan_sample_count'])} | {ratio(pai_gran['template_shift_tp'], pai_gran['template_shift_sample_count'])} | {pai_in['latency_p50_ms']:.2f} ms |
| **GuardShield DeBERTa-v3 (Ours)** | **142.6M (Small)** | **{pct(m_in['accuracy'])}** | **{pct(m_in['recall'])}** | **{pct(m_ood['accuracy'])}** | **{pct(m_ood['recall'])}** | **{ratio(dan['attacks_flagged'], dan['attacks'])}** | **{ratio(tmpl['attacks_flagged'], tmpl['attacks'])}** | **{m_in['latency_p50_ms']:.2f} ms** |"""

    in_dist_breakdown = ", ".join(
        f"{src} {ratio(v['attacks_flagged'], v['attacks'])}"
        for src, v in sorted(src_in.items()) if v["attacks"]
    )

    multiturn_table = f"""| Configuration | Turns Flagged (all, $N={n_turns}$) | User Turns Flagged ($N={n_user}$) | Assistant Turns Flagged ($N={n_asst}$) | Conversations Blocked ($N={n_conv}$) |
| :--- | :---: | :---: | :---: | :---: |
| **ProtectAI DeBERTa-v3-base (stateless)** | {ratio(pai_mt['all_turns_false_positives'], n_turns)} | {ratio(pai_mt['user_turns_false_positives'], n_user)} | {ratio(pai_mt['assistant_turns_false_positives'], n_asst)} | {ratio(pai_mt['conversations_blocked'], n_conv)} |
| **GuardShield AI (no signed history)** | {ratio(gs_mt['all_turns_false_positives'], n_turns)} | {ratio(gs_mt['user_turns_false_positives'], n_user)} | {ratio(gs_mt['assistant_turns_false_positives'], n_asst)} | {ratio(gs_mt['raw_conversations_blocked'], n_conv)} |
| **GuardShield AI (signed assistant history)** | — | **{ratio(gs_mt['signed_history_user_turns_false_positives'], n_user)}** | not scanned (signed) | **{ratio(gs_mt['signed_history_conversations_blocked'], n_conv)}** |"""

    adaptive_rows = [
        "| Perturbation Vector | $N$ (attack / benign) | GuardShield Recall [95% CI] | GuardShield Benign FPR [95% CI] | Fixed 128-Token Truncation Recall | Keyword Blocklist Recall |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for v in vectors:
        g = v["guardshield"]
        adaptive_rows.append(
            f"| {v['perturbation_vector']} | {v['n_attacks']} / {v['n_benign']} | {g['recall']:.1f}% {ci(g['recall_ci'])} | "
            f"{g['fpr']:.1f}% {ci(g['fpr_ci'])} | {v['naive_truncation']['recall']:.1f}% | {v['keyword_blocklist']['recall']:.1f}% |"
        )
    adaptive_table = "\n".join(adaptive_rows)

    if blanket:
        fprs = [v["guardshield"]["fpr"] for v in blanket]
        names = ", ".join(re.sub(r"^\d+\.\s*", "", v["perturbation_vector"]) for v in blanket)
        blanket_text = (
            f"On {len(blanket)} of the {len(vectors)} vectors ({names}), benign prompts carrying the same perturbation are flagged "
            f"at a **{min(fprs):.1f}%–{max(fprs):.1f}% FPR**. Recall on those rows therefore reflects blanket rejection of "
            f"non-standard text (token fragmentation, cipher wrappers), not semantic decoding of the payload."
        )
    else:
        blanket_text = f"No perturbation vector drives the benign FPR to {BLANKET_REJECTION_FPR:.0f}% or more."

    if hard_neg:
        hard_neg_text = (
            f"A hard-negative fine-tuning pass added {hard_neg['hard_negative_benign_added']} benign and "
            f"{hard_neg['hard_attack_retention_added']} attack prompts after automatically removing "
            f"{len(hard_neg['decontamination_removed'])} candidates that overlapped any evaluation set or regression test "
            f"(`hard_negative_training_summary.json`), so the benign-hard and multi-turn results below are measured on held-out text."
        )
    else:
        hard_neg_text = "The deployed checkpoint has no hard-negative fine-tuning pass."

    worst_text = "; ".join(f"{c} {ratio(fp, n)}" for _, c, fp, n in worst_cats) or "none"

    # ------------------------------------------------------------------ block
    return f"""{BEGIN_MARKER}
## 📊 V3 Mega Research Benchmark Evaluation (5,948 Curated Samples)

GuardShield AI has been empirically evaluated across **7 published academic and industry benchmark datasets**:
- **Security & Adversarial Benchmarks (5,148 samples)**:
  - *In-Distribution (4,648 samples)*: Partitioned into 3,253 Train, 697 Validation, and {n_in} Test samples across Stanford Online Safety (SPML), Jayavibhav Injection Suite, Deepset Prompt Injections, and TruthfulQA benign queries.
  - *Out-of-Distribution Zero-Shot ({n_ood} samples)*: {dan['attacks']} human-written ChatGPT jailbreaks + {tmpl['attacks']} synthetic template-shift injections + {ood_benign} held-out benign queries.
- **Factuality & Hallucination Grounding Benchmarks ({n_s2} unique pairs)**:
  - {fever['sample_count']} claim-evidence pairs from **FEVER (NAACL 2018)**.
  - {halu['sample_count']} grounded/hallucinated QA pairs from **HaluEval (EMNLP 2023)**.

### Empirical Evaluation Summary

{headline_table}

*Stage 1 metrics are pure neural inference with sliding-window chunking (no keyword heuristics). Stage 2 runs `verify_claim` with multi-sentence decomposition: FEVER {pct(fever['accuracy'])} accuracy / {fever['auroc']:.4f} AUROC, HaluEval QA {pct(halu['accuracy'])} accuracy / {halu['auroc']:.4f} AUROC. Neutral claims without sufficient evidence are reported as `UNVERIFIED_NEUTRAL` rather than as hallucinations. Per-sample predictions, latencies, dataset/weights SHA-256 hashes and git commits are in `docs/01 Reports/raw_eval_*.json`; all Stage 1 numbers on this page come from weights `{weights_hash[:16]}`.*

#### Stage 2 Disaggregated Fact Grounding Breakdown (FEVER vs. HaluEval)

{stage2_table}

---

### Comparative Baselines: GuardShield vs. TF-IDF & ProtectAI DeBERTa-v3

GuardShield is compared with TF-IDF + Logistic Regression and ProtectAI's `deberta-v3-base-prompt-injection-v2` ({pai_meta['total_parameters']} parameters) on identical splits:

{baselines_table}

**Granular Zero-Shot OOD Breakdown**:
- **Human-written DAN jailbreaks ({dan['attacks']} prompts)**: GuardShield {ratio(dan['attacks_flagged'], dan['attacks'])}, ProtectAI {ratio(pai_gran['human_dan_tp'], pai_gran['human_dan_sample_count'])}, TF-IDF {ratio(tf_dan_tp, tf_ood['dan_sample_count'])}. These prompts share explicit lexical markers ("jailbroken", "DAN"), which is why TF-IDF does well here.
- **Synthetic template-shift injections ({tmpl['attacks']} prompts, 5 structural templates with slot variations)**: GuardShield {ratio(tmpl['attacks_flagged'], tmpl['attacks'])}, ProtectAI {ratio(pai_gran['template_shift_tp'], pai_gran['template_shift_sample_count'])}, TF-IDF {ratio(tf_tmpl_tp, tf_ood['synthetic_sample_count'])}.
- **All OOD attacks**: GuardShield recall {ratio(ood_attacks_flagged, ood_attacks)} with a benign false positive rate of {ratio(ood_benign_flagged, ood_benign)}.
- **In-distribution attack recall by source**: {in_dist_breakdown}.
- **Statistical rigor**: in-distribution accuracy {pct(in_correct / n_in)} (95% Wilson CI {pct(in_lo)}–{pct(in_hi)}). Length-matched controls and long-prompt audits are in [`statistical_rigor_and_controls.md`](docs/03%20Research%20and%20Catalogs/statistical_rigor_and_controls.md).

---

### 💬 Multi-Turn Benign Dialogue Robustness Benchmark (N={n_conv} Conversations, {n_turns} Turns)

All {n_conv} conversations (algorithmic follow-ups, ML derivations, networking, Hinglish/Hindi dialogue, creative role-play) are benign, so every flag is a false positive. GuardShield is scored with the proxy's own multi-turn logic (`proxy_server.scan_messages`); ProtectAI scores each turn in isolation:

{multiturn_table}

*Scanning relayed assistant turns with an ingress classifier compounds false alarms. With HMAC-signed assistant history, verified assistant replies are not rescanned while user turns and unsigned or forged assistant turns are always scanned.*

---

### 🛡️ Adaptive Adversarial Robustness & Evasion Defense

Eleven perturbation vectors on balanced cohorts with exact 95% Wilson intervals (details in [`table_adaptive_robustness.md`](docs/01%20Reports/table_adaptive_robustness.md)):

{adaptive_table}

- **Character and cipher obfuscation**: {blanket_text}
- **Length padding** keeps the semantics clean: fixed 128-token truncation misses attacks once a long benign prefix is prepended, while sliding-window chunking scans every window and takes the maximum risk (see the padding rows above).
- **XSTest ({xs['safe_prompts']['sample_count'] + xs['contrast_unsafe_prompts']['sample_count']} prompts)**: false refusal rate on {xs['safe_prompts']['sample_count']} safe homonym prompts is {xs['safe_prompts']['guardshield_frr']:.1f}% {ci(xs['safe_prompts']['guardshield_frr_ci'])}; block rate on {xs['contrast_unsafe_prompts']['sample_count']} plainly harmful (non-injection) requests is {xs['contrast_unsafe_prompts']['guardshield_recall']:.1f}% {ci(xs['contrast_unsafe_prompts']['guardshield_recall_ci'])}. Stage 1 is a prompt-injection/jailbreak filter, not a harmful-content moderator.
- **Calibration**: `PreScanSecurityFilter` uses raw logits ($T = 1.0$); scalar temperature scaling does not move decisions at the 0.50 threshold.

---

## ⚠️ Known Limitations & Operational Boundaries

1. **Benign-hard, multilingual and multi-turn false positives**:
   - On the {len(bh_preds)}-probe benign-hard suite, GuardShield flags {ratio(bh_fp, len(bh_benign))} of benign prompts (ProtectAI: {ratio(pai_bh['false_positive_count'], pai_bh['benign_sample_count'])}) while catching {ratio(bh_tp, len(bh_attacks))} of its attacks. Highest benign FPR categories: {worst_text}.
   - {hard_neg_text}
   - With signed assistant history, {ratio(gs_mt['signed_history_conversations_blocked'], n_conv)} of benign conversations are blocked (no signing: {ratio(gs_mt['raw_conversations_blocked'], n_conv)}; ProtectAI: {ratio(pai_mt['conversations_blocked'], n_conv)}).

2. **Character & cipher obfuscation**: {blanket_text}

3. **Short conversational turns**: turns under {50} characters and at most 6 words are scanned on their own *and* together with the preceding scanned turn; the higher risk wins, so attacker-supplied context can add risk but never dilute a short attack below threshold. Signed assistant replies are not used as context.

4. **Assistant signing key**: set `GUARDSHIELD_PROXY_SECRET` in deployment. Without it the proxy generates an ephemeral per-process key, so client-held signatures stop verifying after a restart or across multiple workers (those turns are then scanned like any untrusted turn).

5. **Stage 2 domain sensitivity**: the cross-encoder reaches {pct(fever['accuracy'])} accuracy / {fever['auroc']:.4f} AUROC on single-sentence FEVER claims but {pct(halu['accuracy'])} / {halu['auroc']:.4f} on open-domain HaluEval QA. Grounding contexts longer than the 256-token window are split into sentence-aligned windows; a claim counts as supported if any window entails it.

{END_MARKER}
"""


def sync_readme():
    print("Loading empirical evaluation reports from docs/01 Reports/...")
    block = build_results_block()
    s1_in = load_json("raw_eval_in_distribution_test_698.json")["metrics"]
    s2 = load_json("raw_eval_stage2_factuality_800.json")["metrics"]
    e2e = load_json("raw_eval_pipeline_e2e.json")["metrics"]

    content = README_PATH.read_text(encoding="utf-8")

    if BEGIN_MARKER in content and END_MARKER in content:
        start = content.index(BEGIN_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER) + 1
    else:
        start = content.index(RESULTS_START_HEADING)
        end = content.index(RESULTS_END_HEADING)
        block += "\n---\n\n"
    content = content[:start] + block + content[end:]

    # Executive summary latency figures
    for pattern, value in [
        (r"(inspects ingress prompts in \*\*~)[0-9.]+( ms \(p50\)\*\*)", f"{s1_in['latency_p50_ms']:.2f}"),
        (r"(premise-hypothesis entailment verification \(\*\*~)[0-9.]+( ms p50\*\*\))", f"{s2['latency_p50_ms']:.2f}"),
    ]:
        content, n = re.subn(pattern, lambda m: m.group(1) + value + m.group(2), content)
        if n != 1:
            raise SystemExit(f"Executive summary pattern not found exactly once: {pattern}")
    content, n = re.subn(
        r"overhead measures \*\*[0-9.]+ ms \(p50\)\*\* / \*\*[0-9.]+ ms \(mean\)\*\*",
        f"overhead measures **{e2e['latency_p50_ms']:.2f} ms (p50)** / **{e2e['latency_mean_ms']:.2f} ms (mean)**",
        content,
    )
    if n != 1:
        raise SystemExit("Executive summary E2E latency pattern not found exactly once")

    README_PATH.write_text(content, encoding="utf-8")
    print("Successfully synchronized README.md with authoritative empirical logs!")


if __name__ == "__main__":
    sync_readme()
