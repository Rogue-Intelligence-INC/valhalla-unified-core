# Context Flexibility — Maximum Goal

> **Status:** GOAL_IN_PROGRESS  
> **Protocol:** `context-flexibility-max-goal-v1`  
> **Report:** `reports/valhalla_inference/context_flexibility_max_goal.json`

## Goal

One of Valhalla Unified Core's **maximum product goals**:

1. **Flexible context** — session append without re-sending full corpus; internal context grows while wire payload stays small.
2. **Topic continuity** — consecutive questions on the same thread stay on-topic as corpus grows.
3. **Multi-question disambiguation** — batch questions on mixed topics each get the correct sub-answer.

## Three Improvements (v1)

| # | Mechanism | Config |
|---|-----------|--------|
| 1 | **Hybrid follow-up LM** | `decode=hybrid`, `follow_up_decode=lm_patch_on_follow_up` — first turn native retrieval; follow-ups use structure→LM patch on incubated snapshot |
| 2 | **Follow-up-aware retrieval** | `follow_up_decode=native_follow_up_aware` — rank corpus with prior question history (boost current-Q keywords, penalize prior-only hits, recency bias) |
| 3 | **Extended threads** | 10-turn × 3-topic drill with incremental session append |

## A. Context Growth

| Metric | Value |
|--------|-------|
| Seed lines | 4 |
| After 12 appends | **16 lines / 638 chars** |
| Incremental payload (avg) | **~64.3 chars/step** |
| Traditional full prompt | 752 chars (3.62× initial) |

**Takeaway:** High flexibility → internal context scales linearly; transport cost stays ~flat per append.

## B. Extended Topic Continuity (10 turns × 3 topics = 30)

| Architecture | On-topic | Rate |
|--------------|----------|------|
| native_baseline | 29/30 | 96.7% |
| follow_up_aware | 29/30 | 96.7% |
| hybrid_follow_up_lm | 19/30 | 63.3% |
| traditional_lm | 24/30 | 80.0% |

### Improvement deltas

| Comparison | Δ rate |
|------------|--------|
| follow_up_aware vs baseline | +0.0% |
| hybrid_follow_up vs baseline | -33.3% |
| hybrid_follow_up vs traditional | -16.7% |
| follow_up_aware vs traditional | +16.7% |

## C. Multi-Question Disambiguation

9 mixed-topic questions (3 batches):

| Architecture | Correct-topic |
|--------------|---------------|
| native_baseline | 9/9 |
| follow_up_aware | 9/9 |
| hybrid_follow_up_lm | 8/9 |
| traditional_lm | 9/9 |

Batch multi-Q remains strong across architectures; native batch retrieval matches traditional LM.

## Architecture Notes

- **Native baseline** excels at single-shot retrieval and corpus swap sensitivity.
- **Follow-up-aware retrieval** adds session `question_history` + `follow_up_retrieval_boost()` in `native_qa.rs`.
- **Hybrid follow-up LM** routes open follow-ups to `run_lm_one` with pre-incubated `TriadIncubationSnapshot` (structure substrate, not raw prompt RAG).
- **Traditional LM** remains strong on conversational follow-ups when explicit corpus block is injected each turn.

## Reproduce

```bash
cd /path/to/Valhalla
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_context_flexibility_goal.py
```

## Next Steps

- **Production default for dialogue sessions:** `decode=hybrid` + `follow_up_decode=native_follow_up_aware` (beats traditional +16.7pp on 30-turn extended test)
- **Do not use** `lm_patch_on_follow_up` alone for follow-ups without explicit corpus prompt — scored 63.3% vs 96.7% native on extended threads
- Longer threads (12–20 turns) under fair-benchmark corpus
- Combine `core_fusion` with follow-up-aware native for multimodal sessions
