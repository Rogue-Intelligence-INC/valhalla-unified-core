# MCQ hybrid lm_patch scaling ladder — 2026-06-30

**Protocol:** `mcq-ladder-v1` · **Verdict:** `MCQ_LADDER_SCALES`  
**Runner:** `python3 tools/valhalla_inference/test_mcq_ladder_v1.py`  
**JSON:** `mcq_ladder_v1_test.json`

## What changed

Rust `patch_lm.rs` now loads **sharded** Qwen weights (`model.safetensors.index.json` + `model-*-of-*.safetensors`). Previously only single-file `model.safetensors` worked → **Qwen 3B/7B failed silently or at load**.

## Results (fair test MCQ, n=10 fast slice)

| Backbone | Params | Hybrid lm_patch | Notes |
|----------|--------|-----------------|-------|
| Qwen2.5-0.5B-Instruct | 0.5B | **7/10 (70%)** | Same slice as prior 65% on n=20 full MCQ arm |
| Qwen2.5-3B-Instruct | 3.0B | **10/10 (100%)** | Sharded load OK · ~4 min first question |

## Log-linear fit (hybrid MCQ vs log₁₀ params)

| | Value |
|--|-------|
| Slope | **+0.386** acc per log₁₀(params) |
| R² | 1.000 (2 points) |
| 7B projection | **~100%** (saturated on this slice; intercept 0.82 + slope×log₁₀(7)) |

## Interpretation

- **Structure + lm_patch MCQ scales with backbone** on the Qwen2 ladder: 0.5B → 3B is +30pp on the fast slice.
- Valhalla patch is **Qwen2-only** in Rust Candle; Gemma 2B / Phi 3.8B need bake-to-Qwen2 or a separate architecture path (not in this ladder).
- **7B** not downloaded in cache; run `download_backbone_models.py --only qwen --with-7b` then re-run ladder when disk allows (~15 GB).

## Reproduce

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
RUSTFLAGS="-L /opt/cuda/lib64" python3 tools/valhalla_inference/test_mcq_ladder_v1.py --fast
# full fair MCQ (46Q): omit --fast
# trad baseline: .venv-llm/bin/python3 ... --with-trad
```

---

*Rogue Intelligence LNC.*
