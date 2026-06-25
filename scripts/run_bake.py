#!/usr/bin/env python3
"""Valhalla Unified Core — bake HF model (persistent non-isolated fusion)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
BAKE = REPO / "tools/fair_benchmark/bake_trimodal_fusion.py"
FINALIZE = REPO / "tools/valhalla_model_bridge/finalize_hf_repo.py"
PRODUCT = "valhalla-unified-core-v1"
MODELS = PROJECT / "models" / "hf"
REPORTS = PROJECT / "reports"


def main() -> None:
    ap = argparse.ArgumentParser(description="VUC bake → HF")
    ap.add_argument("--phase", default="smoke")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--strength", type=float, default=0.10)
    ap.add_argument("--strong", action="store_true")
    ap.add_argument("--samples-json", type=Path, default=None)
    ap.add_argument("--skip-hf-verify", action="store_true")
    args = ap.parse_args()

    tag = f"Qwen2.5-0.5B-Unified-Core-v1-{args.phase}-s{args.strength:.2f}"
    out_dir = MODELS / tag

    cmd = [
        sys.executable,
        str(BAKE),
        "--phase",
        args.phase,
        "--strength",
        str(args.strength),
        "--out",
        str(out_dir),
    ]
    if args.strong:
        cmd.append("--strong")
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])
    if args.samples_json:
        cmd.extend(["--samples-json", str(args.samples_json)])
    if args.skip_hf_verify:
        cmd.append("--skip-hf-verify")

    subprocess.run(cmd, check=True, cwd=REPO)

    manifest_path = out_dir / "valhalla_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["product"] = PRODUCT
        manifest["unified_core"] = {
            "protocol": PRODUCT,
            "layout": "non_isolated",
            "phase": args.phase,
            "strength": args.strength,
            "baked_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    repo_id = f"Rogue-Intelligence/Qwen2.5-0.5B-Unified-Core-v1"
    finalize_cmd = [
        sys.executable,
        str(FINALIZE),
        str(out_dir),
        "--repo-id",
        repo_id,
    ]
    if args.skip_hf_verify:
        pass  # finalize has no flag; bake already called skip
    else:
        subprocess.run(finalize_cmd, check=True, cwd=REPO)

    bake_src = REPO / "reports/natural_multimodal_potential" / f"trimodal_bake_{args.phase}.json"
    if bake_src.is_file():
        shutil.copy(bake_src, REPORTS / f"bake_{args.phase}.json")

    meta = {
        "product": PRODUCT,
        "model_dir": str(out_dir),
        "repo_id": repo_id,
        "phase": args.phase,
        "strength": args.strength,
    }
    (REPORTS / f"bake_{args.phase}_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\nVUC HF model → {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
