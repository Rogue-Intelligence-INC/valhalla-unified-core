# Valhalla Unified Core — Engineering Technical Whitepaper

**Document type:** Product & systems whitepaper  
**Product:** Valhalla Unified Core (VUC) · ValhallaBase  
**Version:** vuc-engineering-1.0 · **Date:** 2026-06-26  
**Publisher:** Rogue Intelligence LNC.  
**Audience:** ML systems engineers, platform architects, security & compliance reviewers  
**Status:** Claims tied to reproducible JSON artifacts in `reports/`

---

## Abstract

Valhalla Unified Core separates **structure incubation** from **language-model decode**. Context is ingested into a persistent Triad body (Hub, Tile, StemCell, Fate), not flattened into a prompt window. Multimodal tasks are fused in a **single non-isolated session**, producing near-unity cross-modal patch alignment. Open questions are answered by **corpus-grounded native retrieval**; MCQ uses a small LM as a decode head with logprob routing.

On fair-1.2 test evidence (June 2026):

| Capability | Result | Protocol / report |
|------------|--------|-------------------|
| Non-isolated universal core | **107/107** wins vs isolated | `scale_benchmark_test.json` |
| Open retrieval (targeted corpus) | **97%** (30/31) | `scale_benchmark_test.json` |
| Context swap fidelity | **12/12** (100%) | `context_topic_drift_test.json` |
| Cross-topic hallucination (swap + interleave) | **0%** | `context_topic_drift_test.json` |
| 30-turn topic continuity | **96.7%** on-topic; **0** cross-topic hallucinations | `context_topic_drift_extended_test.json` |
| Core fusion QA (12 cross-modal tasks) | **75%** vs **66.7%** baseline | `context_core_fusion.json` |
| MCQ (46, text-only LM logprob) | **63%** | `scale_benchmark_test.json` |

**Production stack:** `ValhallaBase(decode="hybrid", follow_up_decode="native_follow_up_aware", fate_ingress_routing="quad_cycle", fate_qa_feedback=True)`

---

## 1. Design principles

1. **Structure before tokens** — Corpus and multimodal ingress produce a `TriadIncubationSnapshot`; the LM reads a patched snapshot, not raw RAG text alone.
2. **Non-isolated multimodal fusion** — Text, TTS, and image pulses interleave in one session; isolated per-modality fusion is a baseline, not production.
3. **Hybrid decode** — Route by `score_type`: open → native retrieval; mcq/numeric → LM logprob (default).
4. **Auditable answers** — Native open path returns `[corpus:k]` citations tied to ingested lines.
5. **Incremental context** — Session append (~64 chars wire per step) vs resending full prompt history.

---

## 2. Architecture

### 2.1 Stack overview

```
Application / API
       │
       ▼
┌──────────────────────────────────────┐
│ ValhallaBase  (protocol valhalla-base-v1)
│  · context_items / session append
│  · hybrid routing · core_fusion
│  · fate quad_cycle ingress · QA feedback
└──────────────┬───────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
 Native QA            patch_lm (Qwen2.5)
 [corpus:k] retrieval  MCQ logprob / generate
     │                   │
     └─────────┬─────────┘
               ▼
┌──────────────────────────────────────┐
│ Triad: Hub · Tile · StemCell · Fate
│ TriadIncubationSnapshot
└──────────────┬───────────────────────┘
               │ optional bake
               ▼
 HF export (valhalla-unified-core-v1)
 ValhallaLLM loader · valhalla_fused_lm
```

### 2.2 Two deployment surfaces (do not conflate)

| Surface | Entry | Context mechanism | Best for |
|---------|-------|-------------------|----------|
| **ValhallaBase** | `valhalla_base` binary / Python `ValhallaBase` | Triad incubation + session | Context-flexible QA, citations, append |
| **ValhallaLLM** | `loader.ValhallaLLM` / `valhalla_fused_lm` | Baked structure in weights; optional runtime patch | vLLM-style serve of baked HF product |

Context/topic drift benchmarks in this whitepaper use **ValhallaBase** — the context-flexible product path.

### 2.3 Universal core (multimodal fusion)

**Protocol:** `valhalla-universal-core-v1`

| Layout | Method | Shared patch (12 tasks) | Universal score (107 tasks) |
|--------|--------|-------------------------|----------------------------|
| Isolated | Separate sessions per modality | ~0.85 | 0.943 avg |
| **Non-isolated** | One session, interleaved pulses | **~1.00** | **0.964 avg** |

Non-isolated wins **107/107** fair-benchmark tasks. Real TTS + image (espeak, SD-Turbo) increases isolated/non-isolated gap (+0.11 avg Δ vs hash proxies +0.01), confirming value when channels are heterogeneous.

**Protocol:** `context-core-fusion-v2` — optional `core_fusion=true` fuses task modalities into snapshot before decode; fixes multimodal-without-fusion regressions on boundary MCQ items (e.g. chloroplast vs mitochondria).

### 2.4 Fate ingress & learning

**Protocol:** documented in `FATE_INGRESS_ROUTING.md`

- Production default: **`quad_cycle`** — 4/4 Hub quads active per corpus line (25% each).
- **`fate_qa_feedback=true`** — post-answer quality loop; topic→quad prefs differentiate while ingress stays balanced.

---

## 3. Context integrity & hallucination control

**Protocol:** `context-topic-drift-v1` / `v2`  
**Reports:** `context_topic_drift_test.json`, `context_topic_drift_extended_test.json`

### 3.1 Battery A — Context swap (isolated sessions)

Same question, mutually exclusive context bundles (6 pairs × 2 sides = 12 trials). Answer must match active hint and must not contain forbidden cross-topic entities.

| Metric (production arm) | Result |
|-------------------------|--------|
| Swap fidelity | **12/12 (100%)** |
| Cross-topic hallucination | **0/12 (0%)** |

### 3.2 Battery B — Distractor resistance (fair open_retrieval, n=31)

| Context mode | Behavior |
|--------------|----------|
| Targeted (k=8 relevant lines) | **96.8%** accuracy |
| Distractor (k=8, no answer keywords) | **0%** false confidence |
| Minimal (2 generic lines) | Low accuracy (expected) |

System does **not** invent confident answers from wrong corpus when support is absent.

### 3.3 Battery C — Interleaved topic drift

Alternating France/Australia (and physics/chemistry) appends with mid-session probes.

| Metric | Result |
|--------|--------|
| On-topic | **6/6 (100%)** |
| Cross-topic hallucination | **0/6** |

### 3.4 Battery D — Recency trap

Long wrong-topic block + one correct line; probe correct topic.

| Metric | Result |
|--------|--------|
| On-topic | **2/2 (100%)** |

### 3.5 Battery E — Extended follow-up (30 turns)

3 threads × 10 turns, persistent session, production config.

| Arm | On-topic | Cross-topic hallucination |
|-----|----------|---------------------------|
| **production** (`native_follow_up_aware`) | **29/30 (96.7%)** | **0/30 (0%)** |
| hybrid_follow_up_lm (negative control) | 19/30 (63.3%) | 3/30 (10%) |

**Engineering conclusion:** Do not use `lm_patch_on_follow_up` in dialogue products. Single drift failure is corpus truncation (9 vs 9.8), not topic confusion.

---

## 4. Performance summary (fair-1.2 test)

| Slice | n | Metric | Value |
|-------|---|--------|-------|
| open_retrieval | 31 | targeted accuracy | **97%** |
| mcq | 46 | LM logprob | **63%** |
| mcq | 46 | structure mcq_fate | 35% |
| universal core | 107 | non-isolated wins | **107/107** |
| context swap | 12 | fidelity | **100%** |
| extended session | 30 | cross-topic hallucination | **0%** |

---

## 5. Protocol index

| Protocol ID | Purpose |
|-------------|---------|
| `valhalla-base-v1` | Context-flexible base + hybrid decode |
| `valhalla-universal-core-v1` | Isolated vs non-isolated core metrics |
| `context-core-fusion-v2` | Context bundle + core fusion QA |
| `context-topic-drift-v1/v2` | Swap, distractor, interleave, recency, extended follow-up |
| `context-flexibility-max-goal-v1` | 30-turn follow-up-aware vs LM follow-up |
| `scale-benchmark-v1` | 107-task scale core + context MCQ/open |

---

## 6. Reproducibility

From Valhalla monorepo checkout (license required):

```bash
RUSTFLAGS='-L /opt/cuda/lib64' cargo build -p hub-f64 --release \
  --bin valhalla_base --bin valhalla_universal_core

python3 tools/valhalla_inference/test_context_topic_drift.py --phase test --skip-trad
python3 tools/valhalla_inference/test_context_topic_drift.py --battery-e-only --skip-trad
python3 tools/valhalla_inference/run_scale_benchmark.py --phase test --mcq-ablation --skip-core --skip-open
python3 tools/valhalla_inference/test_context_core_fusion.py --limit 12
```

Artifacts sync to this repo under `reports/` for external diligence.

---

## 7. Known limits (engineering honesty)

| Limit | Detail |
|-------|--------|
| MCQ ceiling | 65.2% deploy lm_patch @ 46; structure-only 30.4%; oracle 69.6% |
| Stem/Tile structure | Organ clusters & tile merge **run at runtime**; fair corpus → ~1 mega-cluster / ~11 tiles — **persistent session** drives lift, not functional organ differentiation |
| Core fusion @ 46 MCQ | Multimodal+fusion **56.5%** vs text-only **63%** on hash proxy modalities — fusion is not a universal MCQ booster |
| open_generation | 0% without corpus (by design; not generative LM on Tier B path) |
| Baked-loader path | ValhallaLLM serve does not replicate session append; separate eval needed |
| mcq_fate | 35% — fallback only; ship LM logprob for MCQ MVP |

---

## 8. Legal

Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved. **NOT OPEN SOURCE.**  
See [NON_OPEN_SOURCE.md](../NON_OPEN_SOURCE.md). Commercial licensing: **licensing@rogue-intelligence.com**
