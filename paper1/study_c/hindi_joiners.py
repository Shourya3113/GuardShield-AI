"""
Study C, arm 2 (paper1/SPEC.md section 2): how often the naive canonicalizer deletes Devanagari joiners
(ZWJ U+200D, ZWNJ U+200C) in native-written Hindi, compared with the script-aware canonicalizer.

  python paper1/study_c/hindi_joiners.py     # writes paper1/study_c/hindi_joiners.json

Corpus: the Hindi prompts of the Aya Dataset (`aya_hindi` in configs/sources.json; Apache-2.0), written by
native-speaker annotators. Reported for all Hindi prompts and for the from-scratch ("original-annotations") subset.
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
from guard_audit.canonicalize import naive, script_aware  # noqa: E402

JOINER = re.compile("[‌‍]")


def stats(texts):
    words = [w for t in texts for w in t.split()]
    def lost(f):
        return sum(len(JOINER.findall(t)) - len(JOINER.findall(f(t))) for t in texts)
    return {"texts": len(texts), "texts_with_joiner": sum(bool(JOINER.search(t)) for t in texts),
            "words": len(words), "words_with_joiner": sum(bool(JOINER.search(w)) for w in words),
            "joiners": sum(len(JOINER.findall(t)) for t in texts),
            "joiners_deleted_naive": lost(naive), "joiners_deleted_script_aware": lost(script_aware),
            "texts_changed_naive": sum(naive(t) != t for t in texts),
            "texts_changed_script_aware": sum(script_aware(t) != t for t in texts)}


def main():
    spec = json.loads((BASE_DIR / "configs" / "sources.json").read_text(encoding="utf-8"))["sources"]["aya_hindi"]
    frames = [pd.read_parquet(hf_hub_download(spec["repo"], f, repo_type="dataset", revision=spec["revision"]))
              for f in spec["files"]]
    df = pd.concat(frames)
    hi = df[df[list(spec["filter"])[0]] == list(spec["filter"].values())[0]]
    out = {"source": "aya_hindi", "revision": spec["revision"],
           "all": stats(hi[spec["text_field"]].astype(str).tolist()),
           "original_annotations": stats(hi[hi.annotation_type == "original-annotations"][spec["text_field"]].astype(str).tolist())}
    path = Path(__file__).with_name("hindi_joiners.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
