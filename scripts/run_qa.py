#!/usr/bin/env python3
"""Valhalla Unified Core — fair benchmark QA (actual LM output)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
BIN = REPO / "target/release/valhalla_fused_lm"
MODELS = PROJECT / "models" / "hf"
REPORTS = PROJECT / "reports"
FIXTURES = PROJECT / "fixtures"
FAIR_SUITE = REPO / "tools/fair_benchmark/fair_benchmark_suite.json"


def crossmodal_suite(ids: list[str]) -> Path:
    """Minimal fair suite containing only the given prompt ids."""
    FIXTURES.mkdir(parents=True, exist_ok=True)
    out = FIXTURES / "crossmodal12_suite.json"
    suite = json.loads(FAIR_SUITE.read_text(encoding="utf-8"))
    id_set = set(ids)
    prompts = [p for p in suite["prompts"] if p["id"] in id_set]
    missing = id_set - {p["id"] for p in prompts}
    if missing:
        sys.exit(f"Prompt ids not in fair suite: {sorted(missing)}")
    doc = {
        "prompts": prompts,
        "corpus": suite["corpus"],
        "splits": {"crossmodal12": [p["id"] for p in prompts]},
        "phases": {
            "crossmodal12": {
                "split": "crossmodal12",
                "corpus": "ingest_clean",
                "description": "12Q same-task cross-modal bake eval",
            }
        },
    }
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def default_model(phase: str) -> Path:
    candidates = sorted(MODELS.glob(f"*Unified-Core-v1-{phase}*"), reverse=True)
    if candidates:
        return candidates[0]
    fallback = REPO / "models/hf/Qwen2.5-0.5B-Instruct-Valhalla-TriModal-Fusion-v3-smoke-s0.10"
    return fallback if fallback.is_dir() else MODELS


def main() -> None:
    ap = argparse.ArgumentParser(description="VUC QA on baked HF model")
    ap.add_argument("--phase", default="smoke")
    ap.add_argument("--model", type=Path, default=None)
    ap.add_argument("--show-samples", type=int, default=12)
    ap.add_argument(
        "--cross-modal-report",
        type=Path,
        default=REPORTS / "cross_modal_test.json",
        help="Use per_task ids from cross-modal report (sets phase=crossmodal12)",
    )
    ap.add_argument("--use-cross-modal-ids", action="store_true", default=False)
    args = ap.parse_args()

    phase = args.phase
    suite_path: Path | None = None
    if args.use_cross_modal_ids or phase == "crossmodal12":
        phase = "crossmodal12"
        report = args.cross_modal_report
        if not report.is_file():
            sys.exit(f"Missing cross-modal report: {report}")
        ids = [t["id"] for t in json.loads(report.read_text())["per_task"]]
        suite_path = crossmodal_suite(ids)

    model = args.model or default_model(phase)
    if not model.is_dir() or not (model / "model.safetensors").is_file():
        sys.exit(f"No baked model at {model}. Run run_bake.py first.")

    if not BIN.is_file():
        subprocess.run(
            ["cargo", "build", "-p", "hub-f64", "--release", "--bin", "valhalla_fused_lm"],
            check=True,
            cwd=REPO,
            env={**dict(__import__("os").environ), "RUSTFLAGS": "-L /opt/cuda/lib64"},
        )

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"qa_{phase}.json"

    cmd = [
        str(BIN),
        "--phase",
        phase,
        "--model",
        str(model),
        "--out",
        str(out),
    ]
    if suite_path:
        cmd.extend(["--suite", str(suite_path)])

    subprocess.run(cmd, check=True, cwd=REPO)

    doc = json.loads(out.read_text(encoding="utf-8"))
    summary = doc.get("summary") or {}
    print(f"\n=== VUC QA ({phase}) ===")
    print(f"Model: {model}")
    if summary.get("total"):
        t = summary["total"]
        print(f"Total: {t.get('correct', '?')}/{t.get('n', '?')} ({100*float(t.get('acc', 0)):.1f}%)")
    for k in ("open", "mcq", "numeric"):
        if k in summary and summary[k].get("n"):
            s = summary[k]
            print(f"  {k}: {s['correct']}/{s['n']}")

    rows = doc.get("fused_rows") or doc.get("rows") or []
    print(f"\n--- Sample outputs (first {args.show_samples}) ---")
    for row in rows[: args.show_samples]:
        rid = row.get("id", "?")
        st = row.get("score_type", "?")
        pred = row.get("prediction") or row.get("answer") or row.get("model_output") or ""
        ref = row.get("reference") or row.get("expected") or row.get("gold") or ""
        if not ref and isinstance(row.get("score"), dict):
            ref = row["score"].get("reference") or ""
        ok = row.get("correct")
        print(f"\n[{rid}] ({st}) correct={ok}")
        if ref:
            print(f"  expected: {str(ref)[:200]}")
        print(f"  output:   {str(pred)[:300]}")

    slim = {
        "product": "valhalla-unified-core-v1",
        "model": str(model),
        "phase": phase,
        "summary": summary,
        "sample_outputs": [
            {
                "id": r.get("id"),
                "score_type": r.get("score_type"),
                "correct": r.get("correct"),
                "output": (r.get("prediction") or r.get("answer") or "")[:500],
                "expected": (
                    r.get("reference")
                    or r.get("expected")
                    or (r.get("score") or {}).get("reference")
                    or ""
                )[:500],
            }
            for r in rows[: args.show_samples]
        ],
    }
    (REPORTS / f"qa_{phase}_summary.json").write_text(
        json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n→ {out}")


if __name__ == "__main__":
    main()
