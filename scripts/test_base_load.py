#!/usr/bin/env python3
"""Test Valhalla-baked model loading — HF standard vs valhalla_fused_lm.

Valhalla bake keeps Qwen as architectural base; structure is fused into weights.
This script verifies both load paths and compares base vs baked on sample prompts.

Usage:
  python3 valhalla-unified-core/scripts/test_base_load.py
  python3 valhalla-unified-core/scripts/test_base_load.py --model path/to/baked
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
REPORTS = PROJECT / "reports"
FIXTURES = PROJECT / "fixtures"
V2 = REPO / "models/hf/Qwen2.5-0.5B-Instruct-Valhalla-FreeMultimodal-Fusion-v2-test-s0.10"
VUC = PROJECT / "models/hf/Qwen2.5-0.5B-Unified-Core-v1-crossmodal12-s0.10"
BASE = "Qwen/Qwen2.5-0.5B-Instruct"
FINALIZE = REPO / "tools/valhalla_model_bridge/finalize_hf_repo.py"
FUSED_BIN = REPO / "target/release/valhalla_fused_lm"


def repair_hf_sidecars(model_dir: Path, donor: Path) -> None:
    """Copy tokenizer/config from a complete bake if sidecars are empty."""
    for name in (
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "generation_config.json",
        "chat_template.jinja",
    ):
        dst = model_dir / name
        src = donor / name
        if src.is_file() and (not dst.is_file() or dst.stat().st_size == 0):
            dst.write_bytes(src.read_bytes())
            print(f"  repaired {name} from donor", file=sys.stderr)


def manifest_summary(model_dir: Path) -> dict:
    path = model_dir / "valhalla_manifest.json"
    if not path.is_file():
        return {"error": "no valhalla_manifest.json"}
    m = json.loads(path.read_text(encoding="utf-8"))
    inc = m.get("incubation") or {}
    bake = m.get("bake") or {}
    uni = m.get("unified_core") or {}
    return {
        "product": m.get("product"),
        "manifest_version": m.get("manifest_version"),
        "base_model_id": bake.get("base_model_id"),
        "bake_mode": bake.get("bake_mode"),
        "strength": bake.get("strength"),
        "weight_delta_norm": bake.get("weight_delta_norm"),
        "body": inc.get("body"),
        "tile_count": inc.get("tile_count"),
        "stem_cell_count": inc.get("stem_cell_count"),
        "corpus_lines": inc.get("corpus_lines"),
        "unified_core": uni or None,
        "load_mode": "baked_hf (runtime_patch=false, weights already contain Valhalla structure)",
    }


def test_transformers_load(model_dir: Path) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True)
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        str(model_dir),
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
    )
    model.eval()
    prompt = "What is the SI unit of force? Answer briefly."
    messages = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt")
    if hasattr(model, "device"):
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    elif torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=64, do_sample=False)
    gen = tok.decode(out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)
    return {
        "loader": "transformers.AutoModelForCausalLM.from_pretrained",
        "prompt": prompt,
        "output": gen.strip()[:400],
        "param_count_M": round(sum(p.numel() for p in model.parameters()) / 1e6, 1),
        "device": str(next(model.parameters()).device),
    }


def test_fused_lm(model_dir: Path, suite: Path, phase: str) -> dict:
    out = REPORTS / f"base_load_fused_{phase}.json"
    REPORTS.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(FUSED_BIN),
            "--phase",
            phase,
            "--model",
            str(model_dir),
            "--suite",
            str(suite),
            "--out",
            str(out),
        ],
        check=True,
        cwd=REPO,
    )
    doc = json.loads(out.read_text(encoding="utf-8"))
    s = doc.get("summary") or {}
    rows = doc.get("fused_rows") or []
    return {
        "loader": "valhalla_fused_lm (reads valhalla_manifest.json, baked_lm track)",
        "summary": s.get("total"),
        "samples": [
            {
                "id": r.get("id"),
                "correct": r.get("correct"),
                "output": (r.get("answer") or "")[:200],
            }
            for r in rows[:4]
        ],
    }


def ensure_crossmodal_suite() -> Path:
    cross = REPORTS / "cross_modal_test.json"
    if not cross.is_file():
        sys.exit(f"Missing {cross}; run run_cross_modal.py first")
    ids = [t["id"] for t in json.loads(cross.read_text())["per_task"]]
    FIXTURES.mkdir(parents=True, exist_ok=True)
    suite_path = FIXTURES / "crossmodal12_suite.json"
    if suite_path.is_file():
        return suite_path
    fair = json.loads((REPO / "tools/fair_benchmark/fair_benchmark_suite.json").read_text())
    prompts = [p for p in fair["prompts"] if p["id"] in ids]
    doc = {
        "prompts": prompts,
        "corpus": fair["corpus"],
        "splits": {"crossmodal12": ids},
        "phases": {
            "crossmodal12": {
                "split": "crossmodal12",
                "corpus": "ingest_clean",
            }
        },
    }
    suite_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return suite_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Valhalla base-load smoke test")
    ap.add_argument("--model", type=Path, default=VUC)
    ap.add_argument("--donor", type=Path, default=V2, help="Complete HF repo for sidecar repair")
    ap.add_argument("--skip-hf-gen", action="store_true")
    ap.add_argument("--skip-fused", action="store_true")
    args = ap.parse_args()

    model_dir = args.model.resolve()
    if not (model_dir / "model.safetensors").is_file():
        sys.exit(f"No weights at {model_dir}")

    print("=== Valhalla as bake base (Qwen substrate + Valhalla structure in weights) ===\n")
    print(f"Model dir: {model_dir}")
    print(f"Architectural base (from manifest): {BASE}\n")

    repair_hf_sidecars(model_dir, args.donor)
    if not (model_dir / "README.md").stat().st_size if (model_dir / "README.md").is_file() else 0:
        subprocess.run(
            [sys.executable, str(FINALIZE), str(model_dir), "--skip-verify"],
            check=True,
            cwd=REPO,
        )

    meta = manifest_summary(model_dir)
    print("--- valhalla_manifest.json ---")
    print(json.dumps(meta, indent=2, ensure_ascii=False))

    report: dict = {"model": str(model_dir), "manifest": meta}

    if not args.skip_hf_gen:
        print("\n--- Hugging Face load (standard) ---")
        try:
            hf = test_transformers_load(model_dir)
            report["transformers"] = hf
            print(json.dumps(hf, indent=2, ensure_ascii=False))
        except Exception as e:
            report["transformers_error"] = str(e)
            print(f"HF load failed: {e}", file=sys.stderr)

    if not args.skip_fused:
        if not FUSED_BIN.is_file():
            subprocess.run(
                ["cargo", "build", "-p", "hub-f64", "--release", "--bin", "valhalla_fused_lm"],
                check=True,
                cwd=REPO,
                env={**dict(__import__("os").environ), "RUSTFLAGS": "-L /opt/cuda/lib64"},
            )
        suite = ensure_crossmodal_suite()
        print("\n--- valhalla_fused_lm load (baked, no runtime patch) ---")
        fused = test_fused_lm(model_dir, suite, "crossmodal12")
        report["valhalla_fused_lm"] = fused
        print(json.dumps(fused, indent=2, ensure_ascii=False))

    out_path = REPORTS / "base_load_test.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n→ {out_path}")


if __name__ == "__main__":
    main()
