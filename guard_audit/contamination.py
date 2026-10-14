"""
Contamination audit (paper1/SPEC.md section 3): overlap of every evaluation pool in a run with the training
sources of each auditable guard (configs/training_sources.json).

  python -m guard_audit.contamination --run paper1/runs/obf_main paper1/runs/pids_main

Pools: the base (unperturbed) text of each pair's attack and twin, and the calibration prompts.
Texts are normalized (lowercase, punctuation removed, whitespace collapsed) before comparison.

  verbatim       the normalized text equals a normalized training text, or one full line of it (corpora such as
                 SPML prepend a copied attack as the first line of a longer prompt)
  containment    share of the text's distinct word 8-grams found in one training text (max over training texts)
  jaccard        exact word 8-gram Jaccard with one training text (max over training texts); SPEC's
                 MinHash threshold of 0.8 is applied to the exact value, which MinHash only estimates
  contaminated   verbatim, or containment >= 0.8 (near-duplicate or embedded copy; jaccard >= 0.8 implies it)

Texts under 8 words have no 8-gram and are checked for verbatim copies only: a short generic phrase
("ignore all previous instructions") inside a different training text is not a copy of the evaluated item.
Containment between 0.5 and 0.8 is reported but not flagged; at that level ~10-word texts match on stock phrases.

Per guard and pool, status (SPEC wording) from the guard's corpus usage in configs/training_sources.json:
  known    contaminated items in a corpus the guard trained on in full
  likely   contaminated items only in corpora the guard lists or sampled from
  none     no contaminated item, and the audited corpora are the guard's whole training set
  unknown  no contaminated item, but part of the training data is undisclosed or was not audited

Writes <run>/contamination.json, including each guard's contaminated pair_ids for
`run_audit metrics --exclude-pairs <run>/contamination.json`.
"""

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TRAINING = BASE_DIR / "configs" / "training_sources.json"

NGRAM = 8
CONTAINMENT_FLAG, CONTAINMENT_REPORT, JACCARD_FLAG = 0.8, 0.5, 0.8
SNIPPET_CHARS = 240
_PUNCT = re.compile(r"[^\w\s]|_")


def normalize(text: str) -> str:
    """Lowercase, punctuation removed, whitespace collapsed."""
    return " ".join(_PUNCT.sub(" ", str(text).lower()).split())


def ngrams(words: List[str], n: int) -> set:
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


class OverlapIndex:
    """Exact verbatim / n-gram containment / n-gram Jaccard of a fixed set of texts against streamed documents."""

    def __init__(self, texts: List[str], n: int = NGRAM):
        self.n = n
        self.verbatim: Dict[str, List[int]] = defaultdict(list)
        self.size: List[int] = []  # distinct n-grams per text (0: under n words, verbatim only)
        self.grams: Dict[tuple, List[int]] = defaultdict(list)
        self.first: set = set()    # first words of indexed n-grams, to skip most document positions cheaply
        for i, text in enumerate(texts):
            norm = normalize(text)
            if norm:
                self.verbatim[norm].append(i)
            grams = ngrams(norm.split(), n)
            self.size.append(len(grams))
            for g in grams:
                self.grams[g].append(i)
                self.first.add(g[0])

    def match(self, doc: str) -> List[Tuple[int, bool, float, float]]:
        """[(text index, verbatim, containment, jaccard)] for every indexed text overlapping this document."""
        norm = normalize(doc)
        if not norm:
            return []
        whole = set(self.verbatim.get(norm, ()))
        lines = set()
        if "\n" in doc or "\r" in doc:
            lines = {i for line in doc.splitlines() for i in self.verbatim.get(normalize(line), ())}
        words = norm.split()
        hits: Counter = Counter()
        if not self.first.isdisjoint(words):
            seen = set()
            for j in range(len(words) - self.n + 1):
                if words[j] in self.first:
                    g = tuple(words[j:j + self.n])
                    if g not in seen and g in self.grams:
                        seen.add(g)
                        for i in self.grams[g]:
                            hits[i] += 1
        out = []
        doc_size = len(ngrams(words, self.n)) if hits else 0
        for i in whole | lines | set(hits):
            if i in whole:
                out.append((i, True, 1.0, 1.0))
                continue
            inter = hits.get(i, 0)
            containment = 1.0 if i in lines else inter / self.size[i]
            union = self.size[i] + doc_size - inter
            out.append((i, i in lines, containment, inter / union if union else 0.0))
        return out


# --------------------------------------------------------------------------- corpora
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)) or type(value).__name__ == "ndarray":
        for v in value:
            yield from _strings(v)


def _rows(path: Path, fmt: Optional[str] = None) -> Iterator[Any]:
    suffix = f".{fmt}" if fmt else path.suffix.lower()
    if suffix == ".parquet":
        import pandas as pd
        yield from pd.read_parquet(path).to_dict("records")
    elif suffix == ".csv":
        import pandas as pd
        yield from pd.read_csv(path, keep_default_na=False).to_dict("records")
    elif suffix == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            yield from (json.loads(line) for line in f if line.strip())
    elif suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):  # {"split": [rows]} or a single row
            lists = [v for v in data.values() if isinstance(v, list)]
            data = [r for v in lists for r in v] if lists else [data]
        yield from data
    else:
        raise ValueError(f"unsupported file type: {path}")


def _python_lists(path: Path, names: List[str]) -> List[str]:
    """String lists assigned at module level, read without executing the script."""
    out = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            out.extend(ast.literal_eval(node.value))
    return out


def corpus_files(spec: Dict[str, Any]) -> List[Tuple[Path, Dict[str, Any]]]:
    """Resolves (and downloads, if needed) a corpus' files; returns [(path, provenance)]."""
    kind = spec["type"]
    if kind == "local_json":
        return [(BASE_DIR / p, {"path": p}) for p in spec["paths"]]
    if kind == "python_lists":
        return [(BASE_DIR / spec["path"], {"path": spec["path"]})]
    if kind == "url_json":
        from .sources import _download
        return [(_download(spec["url"], spec["sha256"]), {"url": spec["url"]})]
    if kind == "hf":
        from huggingface_hub import hf_hub_download
        return [(Path(hf_hub_download(spec["repo"], f, repo_type="dataset", revision=spec["revision"])),
                 {"repo": spec["repo"], "revision": spec["revision"], "file": f}) for f in spec["files"]]
    raise ValueError(f"unknown corpus type: {kind}")


def corpus_docs(spec: Dict[str, Any], files: List[Tuple[Path, Dict[str, Any]]]) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yields (training text, metadata). Without `text_fields`, every string in a row is its own document."""
    if spec["type"] == "python_lists":
        for text in _python_lists(files[0][0], spec["names"]):
            yield text, {}
        return
    fields, meta_fields = spec.get("text_fields"), spec.get("meta_fields", [])
    filt = spec.get("filter", {})
    fmt = "json" if spec["type"] == "url_json" else None  # downloads are cached under their SHA-256, without a suffix
    for path, _ in files:
        for row in _rows(path, fmt):
            if not isinstance(row, dict):
                yield from ((s, {}) for s in _strings(row))
                continue
            if any(row.get(k) not in v for k, v in filt.items()):
                continue
            meta = {k: row.get(k) for k in meta_fields if k in row}
            values = [row.get(f) for f in fields] if fields else list(row.values())
            for v in values:
                for s in _strings(v):
                    yield s, meta


# --------------------------------------------------------------------------- pools
def run_pools(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One entry per audited text: the clean base text of each pair member and each calibration prompt."""
    out = []
    for it in items:
        if it["split"] == "eval" and it["condition"] == "clean":
            out.append({"pool": "attack" if it["label"] == 1 else "twin", "id": it["pair_id"],
                        "source": it["source"], "text": it["base_text"]})
        elif it["split"] == "calibration":
            out.append({"pool": "calibration", "id": it["item_id"], "source": it["source"], "text": it["base_text"]})
    return out


def _source_role(entry: Dict[str, Any]) -> str:
    return f"{entry['source']}:{'attack' if entry['pool'] == 'attack' else 'benign'}"


def guard_status(usages: List[str], complete: bool) -> str:
    """usages: corpus usage ('full' / 'listed' / 'sampled') of every corpus with a contaminated item."""
    if "full" in usages:
        return "known"
    if usages:
        return "likely"
    return "none" if complete else "unknown"


def audit(entries: List[Dict[str, Any]], training: Dict[str, Any], corpora: Optional[List[str]] = None,
          log=print) -> Tuple[Dict[str, Any], Dict[str, Dict[int, Dict[str, Any]]]]:
    """Scans every corpus once. Returns (corpus provenance, {corpus: {entry index: best match}})."""
    index = OverlapIndex([e["text"] for e in entries])
    needed = sorted({c for g in training["guards"].values() for c in g["corpora"]})
    if corpora is not None:
        needed = [c for c in needed if c in corpora]
    provenance, best = {}, {}
    for name in needed:
        spec = training["corpora"][name]
        files = corpus_files(spec)
        n_docs, found = 0, {}
        for doc, meta in corpus_docs(spec, files):
            n_docs += 1
            for i, verbatim, containment, jaccard in index.match(doc):
                cur = found.get(i)
                if cur is None or (verbatim, containment, jaccard) > (cur["verbatim"], cur["containment"], cur["jaccard"]):
                    found[i] = {"verbatim": verbatim, "containment": round(containment, 4), "jaccard": round(jaccard, 4),
                                "doc": n_docs - 1, "meta": meta, "snippet": doc[:SNIPPET_CHARS]}
        provenance[name] = {"files": [{**p, "sha256": _sha256(path)} for path, p in files], "n_docs": n_docs}
        if n_docs == 0:
            raise SystemExit(f"corpus {name} yielded no texts; check its text_fields")
        best[name] = found
        log(f"[{name}] {n_docs} training texts, {sum(_flag(m) for m in found.values())} audited texts contaminated")
    return provenance, best


def _flag(m: Dict[str, Any]) -> bool:
    return m["verbatim"] or m["containment"] >= CONTAINMENT_FLAG


def summarize(entries: List[Dict[str, Any]], training: Dict[str, Any], best: Dict[str, Dict[int, Dict[str, Any]]]) -> Dict[str, Any]:
    pools = Counter(e["pool"] for e in entries)
    roles = sorted({_source_role(e) for e in entries})
    guards = {}
    for guard, g in training["guards"].items():
        corpora = [c for c in g["corpora"] if c in best]
        per_pool = {p: {"n": n, "n_verbatim": 0, "n_jaccard80": 0, "n_containment50": 0, "n_containment80": 0,
                        "n_contaminated": 0, "by_corpus": {}} for p, n in pools.items()}
        status_usages: Dict[str, List[str]] = {r: [] for r in roles}
        pairs, calibration, matches = set(), set(), []
        for i, e in enumerate(entries):
            ms = {c: best[c][i] for c in corpora if i in best[c]}
            if not ms:
                continue
            row = per_pool[e["pool"]]
            row["n_verbatim"] += any(m["verbatim"] for m in ms.values())
            row["n_jaccard80"] += any(m["jaccard"] >= JACCARD_FLAG for m in ms.values())
            row["n_containment50"] += any(m["containment"] >= CONTAINMENT_REPORT for m in ms.values())
            row["n_containment80"] += any(m["containment"] >= 0.8 for m in ms.values())
            flagged = {c: m for c, m in ms.items() if _flag(m)}
            if not flagged:
                continue
            row["n_contaminated"] += 1
            for c in flagged:
                row["by_corpus"][c] = row["by_corpus"].get(c, 0) + 1
                status_usages[_source_role(e)].append(g["corpora"][c])
            (calibration if e["pool"] == "calibration" else pairs).add(e["id"])
            top_c, top = max(flagged.items(), key=lambda kv: (kv[1]["verbatim"], kv[1]["containment"], kv[1]["jaccard"]))
            matches.append({"pool": e["pool"], "id": e["id"], "source": e["source"], "text": e["text"],
                            "corpus": top_c, "corpora": sorted(flagged), **{k: top[k] for k in ("verbatim", "containment", "jaccard", "meta", "snippet")}})
        guards[guard] = {
            "complete": g["complete"],
            "corpora": g["corpora"],
            "documentation": g.get("documentation"),
            "status": {r: guard_status(status_usages[r], g["complete"] and len(corpora) == len(g["corpora"])) for r in roles},
            "pools": per_pool,
            "contaminated_pairs": sorted(pairs),
            "contaminated_calibration": sorted(calibration),
            "matches": matches,
        }
    return {"pools": {p: dict(n=n, sources=dict(Counter(e["source"] for e in entries if e["pool"] == p))) for p, n in pools.items()},
            "guards": guards}


def main(argv=None):
    from .run_audit import environment, read_items, sha256_file, write_json
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", nargs="+", required=True, help="run directories (corpora are scanned once for all of them)")
    p.add_argument("--training-sources", default=str(DEFAULT_TRAINING))
    p.add_argument("--corpora", nargs="+", help="audit only these corpora (debugging)")
    args = p.parse_args(argv)
    training = json.loads(Path(args.training_sources).read_text(encoding="utf-8"))

    runs = [Path(r) for r in args.run]
    entries, owner = [], []
    for run in runs:
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        if sha256_file(run / "dataset.jsonl") != manifest["dataset_sha256"]:
            raise SystemExit(f"{run}/dataset.jsonl does not match manifest.json; rebuild it (see the run's README).")
        es = run_pools(read_items(run))
        entries += es
        owner += [run] * len(es)
    provenance, best = audit(entries, training, args.corpora)
    for run in runs:
        idx = [i for i, o in enumerate(owner) if o == run]
        sub = [entries[i] for i in idx]
        sub_best = {c: {j: found[i] for j, i in enumerate(idx) if i in found} for c, found in best.items()}
        result = summarize(sub, training, sub_best)
        write_json(run / "contamination.json", {
            "dataset_sha256": sha256_file(run / "dataset.jsonl"),
            "environment": environment(),
            "method": {"normalization": "lowercase; punctuation removed; whitespace collapsed", "ngram_words": NGRAM,
                       "contaminated": f"verbatim (whole text or one full line) or containment >= {CONTAINMENT_FLAG}",
                       "reported_not_flagged": f"containment >= {CONTAINMENT_REPORT}",
                       "jaccard_threshold": JACCARD_FLAG, "jaccard": "exact word n-gram Jaccard (MinHash estimates it)"},
            "corpora": {c: {**provenance[c], **{k: v for k, v in training["corpora"][c].items() if k in ("notes",)}}
                        for c in provenance},
            **result,
        })
        print(f"Wrote {run / 'contamination.json'}")
        for guard, g in result["guards"].items():
            if g["corpora"]:
                counts = ", ".join(f"{p} {v['n_contaminated']}/{v['n']}" for p, v in g["pools"].items())
                print(f"  {guard}: {counts}; status {g['status']}")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
