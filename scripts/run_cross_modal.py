#!/usr/bin/env python3
"""Same question × three modalities — isolated vs non-isolated compare.

Each task: identical text → encode as text | TTS wav | SD image → Fate core alignment.

Usage:
  python3 valhalla-unified-core/scripts/run_cross_modal.py --phase test --limit 12
  python3 valhalla-unified-core/scripts/run_cross_modal.py --phase test --limit 12 \\
      --samples-json valhalla-unified-core/reports/cross_modal_samples_test.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
RUNNER = REPO / "tools/fair_benchmark/run_universal_core_experiment.py"
REPORTS = PROJECT / "reports"


def slim_per_task(row: dict) -> dict:
    iso = row["isolated"]["metrics"]
    niso = row["non_isolated"]["metrics"]
    return {
        "id": row["task_id"],
        "isolated": {
            "shared_patch": round(iso["shared_patch_pairwise_avg"], 4),
            "text_tts": round(iso["patch_text_audio"], 4),
            "text_image": round(iso["patch_text_image"], 4),
            "tts_image": round(iso["patch_audio_image"], 4),
            "common_core": iso["shares_common_core"],
            "universal_score": round(iso["universal_core_score"], 4),
        },
        "non_isolated": {
            "shared_patch": round(niso["shared_patch_pairwise_avg"], 4),
            "text_tts": round(niso["patch_text_audio"], 4),
            "text_image": round(niso["patch_text_image"], 4),
            "tts_image": round(niso["patch_audio_image"], 4),
            "common_core": niso["shares_common_core"],
            "universal_score": round(niso["universal_core_score"], 4),
        },
        "score_delta": round(row["universal_score_delta"], 4),
        "non_isolated_better": row["non_isolated_better"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="VUC same-task cross-modal compare")
    ap.add_argument("--phase", default="test")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--layout", choices=("compare", "isolated", "non_isolated"), default="compare")
    ap.add_argument("--samples-json", type=Path, default=None)
    ap.add_argument("--save-samples", type=Path, default=None, help="Write encoded samples for reuse")
    args = ap.parse_args()

    cmd = [
        sys.executable,
        str(RUNNER),
        "--layout",
        args.layout,
        "--phase",
        args.phase,
    ]
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])

    samples_path = args.samples_json
    if samples_path is None:
        default_samples = REPORTS / f"cross_modal_samples_{args.phase}.json"
        if default_samples.is_file():
            samples_path = default_samples
    save_samples = args.save_samples or (REPORTS / f"cross_modal_samples_{args.phase}.json")
    if samples_path and samples_path.is_file():
        cmd.extend(["--samples-json", str(samples_path)])
    else:
        cmd.extend(["--save-samples", str(save_samples)])

    subprocess.run(cmd, check=True, cwd=REPO)

    src_summary = REPO / "reports/natural_multimodal_potential" / f"universal_core_{args.layout}_{args.phase}_summary.json"
    src_full = REPO / "reports/natural_multimodal_potential" / f"universal_core_{args.layout}_{args.phase}.json"

    REPORTS.mkdir(parents=True, exist_ok=True)
    if src_summary.is_file():
        shutil.copy(src_summary, REPORTS / f"cross_modal_{args.phase}_summary.json")

    if src_full.is_file():
        data = json.loads(src_full.read_text(encoding="utf-8"))
        if args.layout == "compare":
            tasks = [slim_per_task(o) for o in data.get("samples", [])]
            out = {
                "product": "valhalla-unified-core-v1",
                "phase": args.phase,
                "layout": "compare",
                "task_count": len(tasks),
                "summary": data.get("summary"),
                "per_task": tasks,
            }
            (REPORTS / f"cross_modal_{args.phase}.json").write_text(
                json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"\n=== Cross-modal same-task ({args.phase}, n={len(tasks)}) ===")
            print(f"{'ID':<16} {'iso shared':>10} {'niso shared':>11} {'Δ score':>8} win")
            for t in tasks:
                w = "niso" if t["non_isolated_better"] else "iso"
                print(
                    f"{t['id']:<16} {t['isolated']['shared_patch']:>10.3f} "
                    f"{t['non_isolated']['shared_patch']:>11.3f} "
                    f"{t['score_delta']:>+8.3f} {w}"
                )
            s = data.get("summary") or {}
            if s:
                print(
                    f"\nAvg isolated shared:     {s.get('avg_shared_patch_isolated', 0):.3f}\n"
                    f"Avg non-isolated shared: {s.get('avg_shared_patch_non_isolated', 0):.3f}\n"
                    f"Wins: non-isolated {s.get('non_isolated_wins', 0)} / "
                    f"isolated {s.get('isolated_wins', 0)}"
                )
            print(f"→ {REPORTS / f'cross_modal_{args.phase}.json'}")


if __name__ == "__main__":
    main()
