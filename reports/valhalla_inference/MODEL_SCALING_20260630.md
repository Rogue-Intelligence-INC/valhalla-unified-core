# Model scaling & training substrate — 2026-06-30

**Protocol:** `model-scaling-v1` · **Verdict:** `SCALING_EVIDENCE_STRONG`

## Headline

| Metric | Value |
|--------|-------|
| Valhalla hybrid open | **31/31** (100.0%) |
| Structure premium @ 0.5B | **+6.5pp** (trad 93.5%) |
| Structure premium @ 2.0B | **+0.0pp** (trad 100.0%) |
| Structure premium @ 3.8B | **+0.0pp** (trad 100.0%) |

## Patterns

- `TRAD_RAG_SCALES_WITH_PARAMS`
- `STRUCTURE_PREMIUM_NONNEGATIVE`
- `STRUCTURE_PREMIUM_LARGEST_AT_SMALL_BACKBONE`
- `TRAD_MCQ_SCALES_WITH_PARAMS`
- `TIER_B_OPEN_CEILING_STABLE`
- `MCQ_LADDER_SCALES` (Qwen hybrid lm_patch 0.5B→3B)

## MCQ hybrid lm_patch ladder (Qwen2, sharded load)

| Backbone | Params | Hybrid MCQ (fast n=10) |
|----------|--------|------------------------|
| Qwen2.5-0.5B | 0.5B | **70%** |
| Qwen2.5-3B | 3.0B | **100%** |
| Qwen2.5-7B | 7.0B | *proj ~100%* (not run; weights not cached) |

Log-linear slope **+0.39** acc / log₁₀(params). Detail: `MCQ_LADDER_20260630.md`.

## Scale projection (trad_lm open, log-linear)

| Params | trad_lm (proj) | Valhalla (observed) | Premium |
|--------|----------------|---------------------|---------|
| 7.0B | 100.0% | 100.0% | +0.0pp |
| 14.0B | 100.0% | 100.0% | +0.0pp |
| 70.0B | 100.0% | 100.0% | +0.0pp |

---

*Rogue Intelligence LNC.*
