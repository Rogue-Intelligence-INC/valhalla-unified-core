#!/usr/bin/env python3
"""Valhalla Unified Core — structure experiment (non-isolated only)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
RUNNER = REPO / "tools/fair_benchmark/run_universal_core_experiment.py"
REPORTS = PROJECT / "reports"


def main() -> None:
    ap = argparse.ArgumentParser(description="VUC structure experiment")
    ap.add_argument("--phase", default="smoke")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--samples-json", type=Path, default=None)
    args = ap.parse_args()

    cmd = [
        sys.executable,
        str(RUNNER),
        "--layout",
        "non_isolated",
        "--phase",
        args.phase,
    ]
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])
    if args.samples_json:
        cmd.extend(["--samples-json", str(args.samples_json)])

    subprocess.run(cmd, check=True, cwd=REPO)

    src = REPO / "reports/natural_multimodal_potential" / f"universal_core_non_isolated_{args.phase}_summary.json"
    dst = REPORTS / f"experiment_{args.phase}_summary.json"
    if src.is_file():
        shutil.copy(src, dst)
        print(f"→ {dst}", file=sys.stderr)


if __name__ == "__main__":
    main()
