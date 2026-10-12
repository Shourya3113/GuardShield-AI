"""
Loads attack / benign text pools declared in configs/sources.json.

Source types:
  local_json   - a JSON list in this repository
  hf_parquet   - parquet file(s) from a Hugging Face dataset repo, pinned to a revision
  hf_jsonl     - a JSON-lines file from a Hugging Face dataset repo, pinned to a revision
Labels come from either `constant_label` or `label_field` + `attack_values` (1 = attack).
"""

import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent


def _read_rows(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    kind = spec["type"]
    if kind == "local_json":
        with open(BASE_DIR / spec["path"], "r", encoding="utf-8") as f:
            return json.load(f)

    from huggingface_hub import hf_hub_download
    rows: List[Dict[str, Any]] = []
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


def load_source(name: str, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns [{'text', 'label', 'source', 'source_index'}], de-duplicated on exact text."""
    rows = _read_rows(spec)
    filters = spec.get("filter", {})
    max_chars = spec.get("max_chars")
    out, seen = [], set()
    for i, row in enumerate(rows):
        if any(row.get(k) != v for k, v in filters.items()):
            continue
        text = str(row.get(spec["text_field"], "")).strip()
        if not text or text in seen or (max_chars and len(text) > max_chars):
            continue
        if "constant_label" in spec:
            label = int(spec["constant_label"])
        else:
            label = 1 if row.get(spec["label_field"]) in spec["attack_values"] else 0
        seen.add(text)
        out.append({"text": text, "label": label, "source": name, "source_index": i})
    return out


def load_sources_config(path: Path) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["sources"]
