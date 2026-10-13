"""
Validates the Hindi/Hinglish seed sheet (see GUIDELINES.md) and converts it for the audit harness.

  python paper1/annotation/validate_seeds.py seeds.csv                     # check only
  python paper1/annotation/validate_seeds.py seeds.csv --out seeds.jsonl   # check, then write harness items
  python paper1/annotation/validate_seeds.py seeds.csv --make-blind blind.csv   # 20% sample for blind labelling
  python paper1/annotation/validate_seeds.py seeds.csv --kappa blind.csv        # Cohen's kappa of blind labels

Exit code 1 if any error is found. Warnings are printed but do not fail.
"""

import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

REGISTERS = ["en", "hi_deva", "hi_roman", "hinglish"]
COLUMNS = ["seed_id", "label", "category", "trigger_word", *REGISTERS, "spelling_variant_of",
           "author", "validator", "validation", "notes"]
CATEGORIES = {
    "injection": {"override", "extraction", "roleplay_jailbreak", "policy_bypass", "embedded"},
    "benign": {"everyday", "tech", "education", "creative", "instruction_heavy"},
}
SEED_ID = re.compile(r"^S\d{3,4}v?\d*$")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")


def letters(text):
    return [c for c in text if c.isalpha()]


def devanagari_share(text):
    ls = letters(text)
    return sum(bool(DEVANAGARI.match(c)) for c in ls) / len(ls) if ls else 0.0


def read_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"ERROR: missing columns {missing}. Start from seeds_template.csv.")
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def validate(rows):
    errors, warnings = [], []
    ids = Counter(r["seed_id"] for r in rows)
    texts = Counter((reg, r[reg]) for r in rows for reg in REGISTERS if not r["spelling_variant_of"])
    by_id = {r["seed_id"]: r for r in rows}

    for n, r in enumerate(rows, start=2):  # row 1 is the header
        where = f"row {n} ({r['seed_id'] or 'no id'})"
        if "machine" in r["notes"].lower() or "translat" in r["notes"].lower():
            warnings.append(f"{where}: notes mention translation tools; such rows are excluded from the native set")
        if r["validation"] and r["validation"] not in {"accept", "edit", "reject"}:
            errors.append(f"{where}: validation must be accept, edit or reject")
        if not SEED_ID.match(r["seed_id"]):
            errors.append(f"{where}: seed_id must look like S001 (variants: S001v)")
        if ids[r["seed_id"]] > 1:
            errors.append(f"{where}: duplicate seed_id")
        if r["label"] not in CATEGORIES:
            errors.append(f"{where}: label must be 'benign' or 'injection'")
            continue
        if r["category"] not in CATEGORIES[r["label"]]:
            errors.append(f"{where}: category '{r['category']}' not allowed for {r['label']} "
                          f"(use one of {sorted(CATEGORIES[r['label']])})")
        if r["trigger_word"] not in {"yes", "no"}:
            errors.append(f"{where}: trigger_word must be 'yes' or 'no'")
        elif r["trigger_word"] == "yes" and r["label"] != "benign":
            errors.append(f"{where}: trigger_word=yes is only for benign rows")

        empty = [reg for reg in REGISTERS if not r[reg]]
        if empty:
            errors.append(f"{where}: empty register(s) {empty}")
            continue
        if devanagari_share(r["hi_deva"]) < 0.6:
            errors.append(f"{where}: hi_deva must be mostly Devanagari script")
        for reg in ("en", "hi_roman", "hinglish"):
            if DEVANAGARI.search(r[reg]):
                errors.append(f"{where}: {reg} must not contain Devanagari")
            if not LATIN.search(r[reg]):
                errors.append(f"{where}: {reg} has no Latin letters")
        if r["hi_roman"].lower() == r["hinglish"].lower():
            errors.append(f"{where}: hi_roman and hinglish are identical; hinglish must be code-mixed")
        for reg in REGISTERS[1:]:
            ratio = len(r[reg]) / max(1, len(r["en"]))
            if not 0.4 <= ratio <= 2.5:
                warnings.append(f"{where}: {reg} is {ratio:.1f}x the English length")
        if not r["spelling_variant_of"]:
            for reg in REGISTERS:
                if texts[(reg, r[reg])] > 1:
                    errors.append(f"{where}: {reg} text duplicates another seed")
        else:
            base = by_id.get(r["spelling_variant_of"])
            if base is None:
                errors.append(f"{where}: spelling_variant_of points to unknown seed {r['spelling_variant_of']}")
            elif (r["en"], r["hi_deva"], r["label"]) != (base["en"], base["hi_deva"], base["label"]):
                errors.append(f"{where}: a spelling variant must keep en, hi_deva and label identical to its base seed")
            elif (r["hi_roman"], r["hinglish"]) == (base["hi_roman"], base["hinglish"]):
                errors.append(f"{where}: spelling variant changes nothing")
    return errors, warnings


def summary(rows):
    base = [r for r in rows if not r["spelling_variant_of"]]
    benign = [r for r in base if r["label"] == "benign"]
    print(f"Seeds: {len(base)} (+{len(rows) - len(base)} spelling variants)")
    print(f"  labels:     {dict(Counter(r['label'] for r in base))}")
    print(f"  categories: {dict(Counter(r['category'] for r in base))}")
    print(f"  authors:    {dict(Counter(r['author'] for r in base))}")
    if benign:
        share = sum(r["trigger_word"] == "yes" for r in benign) / len(benign)
        print(f"  trigger-word share of benign: {share:.0%} (target >= 25%)")
    print(f"  validated:  {dict(Counter(r['validation'] or 'pending' for r in base))}")


def write_items(rows, out):
    keep = [r for r in rows if r["validation"] in {"accept", "edit"}]
    with open(out, "w", encoding="utf-8") as f:
        for r in keep:
            for reg in REGISTERS:
                f.write(json.dumps({
                    "item_id": f"{r['seed_id']}:{reg}", "seed_id": r["seed_id"], "condition": reg,
                    "label": 1 if r["label"] == "injection" else 0, "category": r["category"],
                    "trigger_word": r["trigger_word"] == "yes", "text": r[reg],
                    "spelling_variant_of": r["spelling_variant_of"] or None,
                    "author": r["author"], "validator": r["validator"],
                }, ensure_ascii=False) + "\n")
    print(f"Wrote {len(keep)} validated seeds x {len(REGISTERS)} registers -> {out} "
          f"({len(rows) - len(keep)} rows not accepted/edited were skipped)")


def make_blind(rows, out, share=0.2, seed=7):
    base = [r for r in rows if not r["spelling_variant_of"]]
    sample = random.Random(seed).sample(base, max(1, round(share * len(base))))
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed_id", "en", "hinglish", "blind_label"])
        for r in sample:
            w.writerow([r["seed_id"], r["en"], r["hinglish"], ""])
    print(f"Wrote {len(sample)} seeds for blind labelling -> {out}. Fill blind_label with benign/injection without looking at seeds.csv.")


def kappa(rows, blind_path):
    truth = {r["seed_id"]: r["label"] for r in rows}
    with open(blind_path, "r", encoding="utf-8-sig", newline="") as f:
        pairs = [(truth[b["seed_id"]], b["blind_label"].strip()) for b in csv.DictReader(f)
                 if b["blind_label"].strip() and b["seed_id"] in truth]
    if not pairs:
        sys.exit("ERROR: no blind labels filled in")
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    labels = ["benign", "injection"]
    expected = sum((sum(a == l for a, _ in pairs) / n) * (sum(b == l for _, b in pairs) / n) for l in labels)
    k = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    print(f"Blind labels: n={n}, raw agreement={observed:.1%}, Cohen's kappa={k:.3f}")


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--out", help="write harness JSONL (only if there are no errors)")
    p.add_argument("--make-blind", help="write a 20%% blind-labelling sample to this CSV")
    p.add_argument("--kappa", help="compute Cohen's kappa from a filled blind-labelling CSV")
    args = p.parse_args()

    rows = read_rows(Path(args.csv))
    errors, warnings = validate(rows)
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    summary(rows)
    if errors:
        print(f"\n{len(errors)} error(s); fix them and re-run.")
        sys.exit(1)
    print("\nNo errors.")
    if args.make_blind:
        make_blind(rows, args.make_blind)
    if args.kappa:
        kappa(rows, args.kappa)
    if args.out:
        write_items(rows, args.out)


if __name__ == "__main__":
    main()
