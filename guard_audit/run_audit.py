"""
Paired-perturbation guard audit.

  python -m guard_audit.run_audit build   --attack-sources gandalf --benign-sources dolly --out runs/paper1/obf
  python -m guard_audit.run_audit score   --run runs/paper1/obf --guards guardshield protectai_v2 deepset
  python -m guard_audit.run_audit metrics --run runs/paper1/obf
  python -m guard_audit.run_audit report  --run runs/paper1/obf

A run directory holds dataset.jsonl + manifest.json (build), scores/<guard>.jsonl + .meta.json
(score), metrics.json (metrics) and report.md (report). Scoring is resumable; scores produced
against a different dataset version are refused.
"""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from .pairs import expand, length_matched_pairs
from .perturbations import FAMILIES, resolve_families
from .sources import load_source, load_sources_config

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = BASE_DIR / "configs" / "sources.json"
DEFAULT_GUARDS = BASE_DIR / "configs" / "guards.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def environment() -> Dict[str, Any]:
    try:
        commit = subprocess.check_output(["git", "describe", "--always", "--dirty", "--abbrev=40"],
                                         cwd=str(BASE_DIR), stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "unknown"
    env = {"git_commit": commit, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "python": platform.python_version(), "platform": platform.platform()}
    try:
        import torch
        import transformers
        env.update(torch=torch.__version__, transformers=transformers.__version__,
                   device=torch.cuda.get_device_name(0) if torch.cuda.is_available()
                   else f"mps ({platform.processor() or 'Apple Silicon'})" if torch.backends.mps.is_available() else "cpu")
    except ImportError:
        pass
    return env


def read_items(run: Path) -> List[Dict[str, Any]]:
    with open(run / "dataset.jsonl", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- build
def cmd_build(args):
    sources = load_sources_config(Path(args.sources))
    attacks, benigns = [], []
    for name in args.attack_sources:
        attacks += [r for r in load_source(name, sources[name]) if r["label"] == 1]
    for name in args.benign_sources:
        benigns += [r for r in load_source(name, sources[name]) if r["label"] == 0]
    attack_texts = {a["text"] for a in attacks}
    benigns = [b for b in benigns if b["text"] not in attack_texts]

    pairs, calibration = length_matched_pairs(attacks, benigns, args.n_pairs, args.calibration_size, args.seed)
    families = resolve_families(args.families)
    items = expand(pairs, calibration, families)

    run = Path(args.out)
    run.mkdir(parents=True, exist_ok=True)
    with open(run / "dataset.jsonl", "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    length_gap = [abs(len(p["attack"]["text"]) - len(p["benign"]["text"])) for p in pairs]
    write_json(run / "manifest.json", {
        "dataset_sha256": sha256_file(run / "dataset.jsonl"),
        "args": vars(args) | {"func": None},
        "source_specs": {n: sources[n] for n in set(args.attack_sources + args.benign_sources)},
        "pool_sizes": {"attacks": len(attacks), "benign": len(benigns)},
        "n_pairs": len(pairs), "n_calibration": len(calibration),
        "families": [f.name for f in families],
        "median_pair_length_gap_chars": sorted(length_gap)[len(length_gap) // 2],
        "n_items": len(items),
        "environment": environment(),
    })
    print(f"Built {len(pairs)} pairs x {len(families)} conditions + {len(calibration)} calibration items -> {run}")


# --------------------------------------------------------------------------- score
def cmd_score(args):
    run = Path(args.run)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    dataset_sha = sha256_file(run / "dataset.jsonl")
    if dataset_sha != manifest["dataset_sha256"]:
        raise SystemExit("dataset.jsonl no longer matches manifest.json; rebuild the run.")
    items = read_items(run)
    guard_specs = json.loads(Path(args.guards_config).read_text(encoding="utf-8"))["guards"]
    unknown = [g for g in args.guards if g not in guard_specs]
    if unknown:
        raise SystemExit(f"Unknown guards {unknown}; see {args.guards_config}")

    lock = run / "scores" / ".lock"
    _acquire_lock(lock)
    try:
        _score_guards(args, run, items, guard_specs, dataset_sha)
    finally:
        lock.unlink(missing_ok=True)


def _acquire_lock(lock: Path):
    """One scorer per run directory: concurrent scorers would fight over the GPU and append to the same files."""
    import os
    import psutil
    lock.parent.mkdir(parents=True, exist_ok=True)
    me = f"{platform.node()}:{os.getpid()}"
    if lock.exists():
        host, _, pid = lock.read_text().strip().rpartition(":")
        if host == platform.node() and pid.isdigit() and psutil.pid_exists(int(pid)):
            raise SystemExit(f"Another scorer (pid {pid}) is already running on {lock.parent.parent}; wait for it or stop it.")
        lock.unlink()  # stale: crashed run, or written on another machine (e.g. a disconnected Colab session)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"Another scorer just started on {lock.parent.parent}.")
    os.write(fd, me.encode())
    os.close(fd)


def _score_guards(args, run, items, guard_specs, dataset_sha):
    from .guards import build_guard
    for name in args.guards:
        out = run / "scores" / f"{name}.jsonl"
        meta_path = run / "scores" / f"{name}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else None
        if args.overwrite:
            out.unlink(missing_ok=True)
        elif meta and meta["dataset_sha256"] != dataset_sha:
            raise SystemExit(f"{out} was scored on a different dataset; pass --overwrite to rescore.")
        done: Dict[str, float] = {}
        if out.exists():
            done = {r["item_id"]: r["score"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())}

        todo = [it for it in items if it["item_id"] not in done]
        if not todo:
            print(f"[{name}] already complete ({len(done)} items)")
            continue
        resumed_from = len(done)
        spec = dict(guard_specs[name])
        if args.batch_size:
            spec["batch_size"] = args.batch_size
        guard = build_guard(name, spec)
        unique_texts = list(dict.fromkeys(it["text"] for it in todo))
        print(f"[{name}] scoring {len(todo)} items ({len(unique_texts)} unique texts)")
        write_json(meta_path, {"guard": guard.info(), "dataset_sha256": dataset_sha, "status": "in_progress"})
        start = time.perf_counter()
        text_score: Dict[str, float] = {}
        for i in range(0, len(unique_texts), args.chunk):
            chunk = unique_texts[i:i + args.chunk]
            text_score.update(zip(chunk, guard.score(chunk)))
            with open(out, "a", encoding="utf-8") as f:
                for it in todo:
                    if it["text"] in text_score and it["item_id"] not in done:
                        done[it["item_id"]] = text_score[it["text"]]
                        f.write(json.dumps({"item_id": it["item_id"], "score": done[it["item_id"]]}) + "\n")
            print(f"  {min(i + args.chunk, len(unique_texts))}/{len(unique_texts)}", flush=True)
        elapsed = time.perf_counter() - start
        write_json(meta_path, {"guard": guard.info(), "dataset_sha256": dataset_sha, "status": "complete",
                               "environment": environment(), "resumed_from_items": resumed_from,
                               "scoring_seconds": round(elapsed, 2), "texts_per_second": round(len(unique_texts) / elapsed, 2)})
        del guard
        try:
            import torch
            torch.cuda.empty_cache()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except ImportError:
            pass


# --------------------------------------------------------------------------- metrics
def cmd_metrics(args):
    from .metrics import guard_metrics
    run = Path(args.run)
    dataset_sha = sha256_file(run / "dataset.jsonl")
    items = read_items(run)
    exclude = set()
    if args.exclude_over_limit:
        over = run / "tokens" / "over_limit_pairs.json"
        if not over.exists():
            raise SystemExit("Run the tokens command first: python -m guard_audit.run_audit tokens --run ...")
        exclude = set(json.loads(over.read_text(encoding="utf-8"))["pairs"])
        print(f"Excluding {len(exclude)} pairs over a classifier's input limit")
    results = {}
    for meta_path in sorted((run / "scores").glob("*.meta.json")):
        name = meta_path.name[:-len(".meta.json")]
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta["dataset_sha256"] != dataset_sha:
            raise SystemExit(f"Scores for {name} were produced on a different dataset; rescore with --overwrite.")
        if meta.get("status") != "complete":
            raise SystemExit(f"Scoring for {name} is incomplete; re-run the score command to resume it.")
        scores = {r["item_id"]: r["score"] for r in
                  map(json.loads, (run / "scores" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines())}
        results[name] = {"guard": meta["guard"],
                         **guard_metrics(items, scores, meta["guard"].get("default_threshold"),
                                         reference_condition=args.reference, n_boot=args.n_boot, seed=args.seed,
                                         exclude_pairs=exclude)}
        print(f"[{name}] metrics computed")
    out_name = "metrics_under_limit.json" if args.exclude_over_limit else "metrics.json"
    write_json(run / out_name, {"dataset_sha256": dataset_sha, "environment": environment(),
                                "excluded_pairs": sorted(exclude), "guards": results})


# --------------------------------------------------------------------------- tokens
def cmd_tokens(args):
    from .tokens import input_limit, token_stats, tokenizer_counter
    run = Path(args.run)
    items = read_items(run)
    specs = json.loads(Path(args.guards_config).read_text(encoding="utf-8"))["guards"]
    over_all = set()
    for name in args.guards:
        try:
            counter = tokenizer_counter(name, specs[name], BASE_DIR)
        except Exception as exc:
            print(f"[{name}] skipped: {exc}")
            continue
        stats = token_stats(items, counter, input_limit(specs[name]))
        over_all.update(stats["over_limit_pairs"])
        write_json(run / "tokens" / f"{name}.json", stats)
        print(f"[{name}] limit={stats['limit']} pairs over limit={len(stats['over_limit_pairs'])}")
    write_json(run / "tokens" / "over_limit_pairs.json", {"guards": args.guards, "pairs": sorted(over_all)})
    print(f"{len(over_all)} pairs exceed at least one classifier's input limit")


# --------------------------------------------------------------------------- report
def _fmt(x, pct=True):
    if x is None or (isinstance(x, float) and x != x):
        return "—"
    return f"{x * 100:.1f}" if pct else f"{x:.3f}"


def cmd_report(args):
    run = Path(args.run)
    m = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    guards = m["guards"]
    if not guards:
        (run / "report.md").write_text(f"# Paired audit report: `{run.name}`\n\nNo guard has complete scores yet.\n",
                                       encoding="utf-8")
        print(f"No scored guards; wrote an empty {run / 'report.md'}")
        return
    conditions = [c for c in FAMILIES if any(c in g["conditions"] for g in guards.values())]
    extra = sorted({c for g in guards.values() for c in g["conditions"]} - set(conditions))
    conditions += extra
    policy = args.policy
    lines = [f"# Paired audit report: `{run.name}`", "",
             f"Dataset `{m['dataset_sha256'][:16]}`, commit `{m['environment']['git_commit'][:12]}`. "
             f"Threshold policy for TPR/FPR/PJA: **{policy}** (calibrated on held-out clean benign prompts unless `default`).", ""]

    def matrix(title, getter, pct=True):
        lines.extend([f"## {title}", "", "| Guard | " + " | ".join(conditions) + " |",
                      "| :--- | " + " | ".join([":---:"] * len(conditions)) + " |"])
        for name, g in guards.items():
            row = [_fmt(getter(g["conditions"][c]), pct) if c in g["conditions"] else "—" for c in conditions]
            lines.append(f"| {name} | " + " | ".join(row) + " |")
        lines.append("")

    def labels(title, getter, names):
        lines.extend([f"## {title}", "", "| Guard | " + " | ".join(conditions) + " |",
                      "| :--- | " + " | ".join([":---:"] * len(conditions)) + " |"])
        for name, g in guards.items():
            row = [names.get(getter(g["conditions"][c]), "—") if c in g["conditions"] else "—" for c in conditions]
            lines.append(f"| {name} | " + " | ".join(row) + " |")
        lines.append("")

    pol = lambda c: c["policies"].get(policy, {})
    matrix("Within-condition AUROC (attack vs. benign twin)", lambda c: c["auroc"], pct=False)
    matrix(f"Paired joint accuracy (%) at {policy}", lambda c: pol(c).get("pja", {}).get("value"))
    matrix(f"Attack recall / TPR (%) at {policy}", lambda c: pol(c).get("tpr", {}).get("value"))
    matrix(f"Benign twin FPR (%) at {policy}", lambda c: pol(c).get("fpr", {}).get("value"))
    matrix(f"FPR (%) after re-thresholding each condition to the {m['guards'][next(iter(guards))]['reference_condition']} TPR",
           lambda c: pol(c).get("fpr_at_ref_tpr", {}).get("fpr"))
    matrix("FPR (%) at the threshold catching 90% of the condition's attacks (threshold-free)", lambda c: c.get("fpr_at_tpr90"))
    labels(f"Intent signal (pre-registered; SPEC section 5)", lambda c: c.get("signal"),
           {"intact": "intact", "degraded": "degraded", "destroyed": "**destroyed**"})
    labels(f"Failure mode at {policy} (pre-registered; SPEC section 5)", lambda c: pol(c).get("failure_mode"),
           {"stable": "·", "fail_closed": "**closed**", "fail_open": "**open**", "both": "**both**"})
    first = next(iter(guards.values()))["conditions"]
    lines.extend(["## Length confound (AUROC of character length, attack vs twin; 0.5 = none)", "",
                  "| " + " | ".join(conditions) + " |", "| " + " | ".join([":---:"] * len(conditions)) + " |",
                  "| " + " | ".join(_fmt(first[c].get("length_auroc"), pct=False) if c in first else "—" for c in conditions) + " |", ""])
    (run / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {run / 'report.md'}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(required=True)

    b = sub.add_parser("build", help="build the paired dataset")
    b.add_argument("--sources", default=str(DEFAULT_SOURCES))
    b.add_argument("--attack-sources", nargs="+", required=True)
    b.add_argument("--benign-sources", nargs="+", required=True)
    b.add_argument("--families", nargs="+", default=["all"])
    b.add_argument("--n-pairs", type=int, default=500)
    b.add_argument("--calibration-size", type=int, default=1000)
    b.add_argument("--seed", type=int, default=13)
    b.add_argument("--out", required=True)
    b.set_defaults(func=cmd_build)

    s = sub.add_parser("score", help="score the dataset with one or more guards (resumable)")
    s.add_argument("--run", required=True)
    s.add_argument("--guards", nargs="+", required=True)
    s.add_argument("--guards-config", default=str(DEFAULT_GUARDS))
    s.add_argument("--chunk", type=int, default=256)
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--batch-size", type=int, help="override every guard's batch size (e.g. 64 on a large GPU)")
    s.set_defaults(func=cmd_score)

    mt = sub.add_parser("metrics", help="compute metrics for every scored guard")
    mt.add_argument("--run", required=True)
    mt.add_argument("--reference", default="clean")
    mt.add_argument("--n-boot", type=int, default=1000)
    mt.add_argument("--seed", type=int, default=0)
    mt.add_argument("--exclude-over-limit", action="store_true",
                    help="drop pairs over any classifier's input limit (needs the tokens command); writes metrics_under_limit.json")
    mt.set_defaults(func=cmd_metrics)

    t = sub.add_parser("tokens", help="token counts, truncation and length confound per guard tokenizer")
    t.add_argument("--run", required=True)
    t.add_argument("--guards", nargs="+", required=True)
    t.add_argument("--guards-config", default=str(DEFAULT_GUARDS))
    t.set_defaults(func=cmd_tokens)

    r = sub.add_parser("report", help="render markdown tables from metrics.json")
    r.add_argument("--run", required=True)
    r.add_argument("--policy", default="fpr@0.05")
    r.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
