"""
Loads attack / benign text pools declared in configs/sources.json.

Source types:
  local_json   - a JSON list in this repository
  hf_parquet   - parquet file(s) from a Hugging Face dataset repo, pinned to a revision
  hf_jsonl     - a JSON-lines file from a Hugging Face dataset repo, pinned to a revision
  url_csv      - CSV file(s) at commit-pinned URLs; each file's SHA-256 must match `sha256`
Labels come from either `constant_label` or `label_field` + `attack_values` (1 = attack).

Row selection, applied in this order:
  filter       - {field: value or [allowed values]}
  exclude      - {field: [rejected values]}
  one_per      - keep one row per value of this field (e.g. a seed id shared by paraphrases),
                 the first after sorting by `one_per_order` (a list of fields)
  max_chars    - drop longer texts
`origin_field` names a column (e.g. an upstream sub-source) that build counts in the manifest.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = Path.home() / ".cache" / "guard_audit" / "sources"


def _download(url: str, sha256: str) -> Path:
    path = CACHE_DIR / sha256
    if not path.exists():
        import urllib.request
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
        got = hashlib.sha256(data).hexdigest()
        if got != sha256:
            raise ValueError(f"{url}: SHA-256 {got} does not match the pinned {sha256}")
        path.write_bytes(data)
    return path


def _read_rows(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    kind = spec["type"]
    if kind == "local_json":
        with open(BASE_DIR / spec["path"], "r", encoding="utf-8") as f:
            return json.load(f)
    if kind == "url_csv":
        import pandas as pd
        rows: List[Dict[str, Any]] = []
        for f in spec["files"]:
            path = _download(f["url"], f["sha256"])
            rows.extend(pd.read_csv(path, keep_default_na=False).to_dict("records"))
        return rows

    from huggingface_hub import hf_hub_download
    rows = []
    for filename in spec["files"]:
        path = hf_hub_download(spec["repo"], filename, repo_type="dataset", revision=spec["revision"])
        if kind == "hf_parquet":
            import pandas as pd
            rows.extend(pd.read_parquet(path).to_dict("records"))
        elif kind == "hf_jsonl":
            with open(path, "r", encoding="utf-8") as f:
                rows.extend(json.loads(line) for line in f if line.strip())
        else:
            raise ValueError(f"Unknown source type: {kind}")
    return rows


def _keep(row: Dict[str, Any], spec: Dict[str, Any]) -> bool:
    for k, v in spec.get("filter", {}).items():
        if row.get(k) not in (v if isinstance(v, list) else [v]):
            return False
    return not any(row.get(k) in v for k, v in spec.get("exclude", {}).items())


def load_source(name: str, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns [{'text', 'label', 'source', 'source_index'}], de-duplicated on exact text."""
    rows = [(i, row) for i, row in enumerate(_read_rows(spec)) if _keep(row, spec)]
    if "one_per" in spec:
        order = spec.get("one_per_order", [])
        rows.sort(key=lambda r: tuple(str(r[1].get(k, "")) for k in order) + (r[0],))
        seen_groups, kept = set(), []
        for i, row in rows:
            if row.get(spec["one_per"]) not in seen_groups:
                seen_groups.add(row.get(spec["one_per"]))
                kept.append((i, row))
        rows = sorted(kept)
    max_chars = spec.get("max_chars")
    out, seen = [], set()
    for i, row in rows:
        text = str(row.get(spec["text_field"], "")).strip()
        if not text or text in seen or (max_chars and len(text) > max_chars):
            continue
        if "constant_label" in spec:
            label = int(spec["constant_label"])
        else:
            label = 1 if row.get(spec["label_field"]) in spec["attack_values"] else 0
        seen.add(text)
        item = {"text": text, "label": label, "source": name, "source_index": i}
        if "origin_field" in spec:
            item["origin"] = row.get(spec["origin_field"])
        out.append(item)
    return out


def load_sources_config(path: Path) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["sources"]
