# MCQ hybrid lm_patch scaling ladder — 2026-06-30

**Protocol:** `mcq-ladder-v1` · **Verdict:** `MCQ_LADDER_SCALES`  
**Runner:** `python3 tools/valhalla_inference/test_mcq_ladder_v1.py`  
**JSON:** `mcq_ladder_v1_test.json`  
**Interpretation:** [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](VALID_BENCHMARKS_INTERPRETATION_20260630.md) §1.5

## What changed

Rust `patch_lm.rs` now loads **sharded** Qwen weights (`model.safetensors.index.json` + `model-*-of-*.safetensors`).

## Results

### Full fair MCQ (n=46) — **canonical for external cite**

| Backbone | Params | Hybrid lm_patch | Run |
|----------|--------|-----------------|-----|
| Qwen2.5-0.5B-Instruct | 0.5B | **30/46 (65.2%)** | industry 2026-06-30 |
| Qwen2.5-3B-Instruct | 3.0B | **45/46 (97.8%)** | industry 2026-06-30 |

### Fast slice (n=10) — smoke only, do not mix with 46Q

| Backbone | Result | Note |
|----------|--------|------|
| 0.5B | 7/10 (70%) | prior smoke run |
| 3.0B | 10/10 (100%) | prior smoke run |

## Log-linear fit (hybrid MCQ vs log₁₀ params, 46Q run)

| | Value |
|--|-------|
| Slope | **+0.419** acc per log₁₀(params) |
| R² | 1.000 (2 points) |

## Because

- MCQ via Hybrid **logprob** on lm_patch; larger Qwen → stronger language prior on fair 46Q.
- Orthogonal to RAGTruth/needle (no corpus; tests patch scaling only).

## Reproduce

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
RUSTFLAGS="-L /opt/cuda/lib64" python3 tools/valhalla_inference/test_mcq_ladder_v1.py
# smoke: add --fast
```

---

*Rogue Intelligence LNC.*
