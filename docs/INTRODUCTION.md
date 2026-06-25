# Valhalla Unified Core — Detailed Introduction

**Version:** 1.0 · **Date:** 2026-06-19  
**Status:** Proprietary product documentation — NOT open source

---

## 1. Executive summary

Large language models treat multimodal input as **late fusion**: separate encoders, shared transformer, token generation. Valhalla Unified Core (VUC) inverts part of that stack. We incubate **structure first** — Hub, Tile, StemCell, and Fate operating on algebraic body ports — and only then attach a small LM as an optional **decode head**.

The central claim is practical, not metaphorical:

> **When the same task is expressed as text, TTS, and image inside one Triad session, cross-modal patch vectors align near 1.0; when modalities are isolated and fused afterward, alignment stays near 0.85.**

That gap is reproducible at scale (107 fair-benchmark tasks, 100% non-isolated wins). VUC packages the winning layout for bake, deployment, and context-aware inference via ValhallaBase.

---

## 2. Problem statement

| Limitation | Typical transformer stack | VUC approach |
|------------|---------------------------|--------------|
| Cross-modal alignment | Embedding-space cosine in LM layers | Fate patch vectors after body incubation |
| Context | Prompt tokens only | Corpus lines + multimodal context items + session append |
| Same-task consistency | Independent modality forwards | Single-session interleaved pulses |
| Open vs MCQ | One decode path | Hybrid: native retrieval vs LM logprob / mcq_fate |
| Deployment | Full finetune or adapter soup | Bake structure into HF weights once; optional runtime patch |

---

## 3. Architecture

### 3.1 Triad body (structure substrate)

All modalities ground into **body front ports** (text hash, audio features, image features) and feed:

- **Hub** — routing and preference vectors  
- **Tile** — local pattern completion  
- **StemCell** — organ-level clustering  
- **Fate** — patch vector export for LM surgery or native QA  

Incubation produces a **TriadIncubationSnapshot** — frozen Tile/Stem state forked per question.

### 3.2 Universal core — isolated vs non-isolated

**Isolated layout** (`valhalla-universal-core-v1`):

1. Run text-only incubation → patch A  
2. Run TTS-only incubation → patch B  
3. Run image-only incubation → patch C  
4. Fuse → measure shared patch pairwise average (~0.85 in cross-modal 12)

**Non-isolated layout** (VUC production layout):

1. Open **one** Triad session  
2. Interleave pulses: text → TTS → image → mixed → repeat  
3. Measure patches after each pulse in-session  
4. Shared patch pairwise average → **~1.00**  

At full test scale (107 tasks): avg universal score **0.964** (non-isolated) vs **0.943** (isolated).

### 3.3 ValhallaBase — context-flexible inference

Protocol: `valhalla-base-v1`

| Feature | Description |
|---------|-------------|
| **Context flex** | Text lines and multimodal `context_items[]` build the incubation snapshot |
| **Hybrid routing** | `open` → native memory retrieval; `mcq` → LM patch logprob (default) or `structure_fate` |
| **Session append** | `append_lines` / `append_items` extend snapshot; fingerprint changes per append |
| **Core fusion** | After context incubation, fuse task text/TTS/image into snapshot before decode |

JSON stdin/stdout API via `valhalla_base` binary.

### 3.4 Context × core fusion pipeline

Protocol: `context-core-fusion-v2`

Per task:

1. **Context layer** — fair corpus lines + sample text/audio/image as context items  
2. **Core layer** — non-isolated universal core metrics on task modalities  
3. **Decode layer** — ValhallaBase hybrid QA  

At 12 cross-modal tasks: core fusion **9/12** QA vs baseline **8/12**; at 46 MCQ full scale LM patch (**63%**) still beats structure-only mcq_fate (**35%**) — LM remains the MCQ head until mcq_fate tuning catches up.

### 3.5 Bake and HF export

Non-isolated incubation over fair corpus + multimodal samples → `bake_valhalla_model` → Hugging Face repo with `valhalla_manifest.json`. Product tag: **`valhalla-unified-core-v1`**.

Runtime can load baked weights only (no surgery) or apply runtime patch per context bundle.

---

## 4. Benchmarks & evidence

### 4.1 Universal core @ 107 tasks

- Non-isolated wins: **107 / 107**  
- Avg shared patch: **1.000** (non-iso) vs **0.980** (iso)  
- Open subset avg Δ universal score: **+0.022**  
- MCQ subset avg Δ universal score: **+0.021**  

### 4.2 Real modalities (espeak + SD-Turbo, 12 tasks)

| Encoding | Isolated uni | Non-iso uni |
|----------|--------------|-------------|
| Hash text proxies | 0.966 | 0.976 |
| Real TTS + image | 0.769 | 0.877 |

Real modalities increase cross-channel heterogeneity (lower isolated score) but **non-isolated fusion gain is larger** (+0.11 avg delta vs +0.01), confirming the production layout matters most when channels are genuinely different.

### 4.3 Context capability @ 61 open tasks

| Slice | Targeted context accuracy |
|-------|---------------------------|
| **open_retrieval** (31) | **97%** (30/31) |
| open_generation (30) | 0% (expected — no corpus support) |
| distractor context | 0% (does not hallucinate wrong corpus) |

Overall open accuracy (~49%) is dominated by generation items; **retrieval slice is near ceiling**.

### 4.4 MCQ @ 46 tasks

| Decode path | Accuracy |
|-------------|----------|
| Hybrid + LM logprob | **63%** |
| Hybrid + structure mcq_fate | 35% |

Recommendation: ship **LM logprob MCQ** for MVP; keep structure path for zero-LM edge deployments.

---

## 5. How this relates to Valhalla monorepo

VUC is a **product line**, not a fork of physics/simulation work (S-wind, E7-φ, etc.).

| Component | Monorepo path |
|-----------|---------------|
| `valhalla_universal_core` | `manifestsys/hub-f64/src/bin/` |
| `valhalla_base` | `manifestsys/hub-f64/src/valhalla_base.rs` |
| Fusion logic | `free_multimodal_fate.rs` |
| Inference tools | `tools/valhalla_inference/` |
| Fair benchmark | `tools/fair_benchmark/` |

This repository holds **protocol docs, scripts, reports, and intro assets** suitable for private GitHub and investor diligence. Binaries and full runtime stay in the main Valhalla checkout under license.

---

## 6. Roadmap (internal)

1. Fix crossmodal12 bake safetensors corruption; validate vLLM-style load end-to-end  
2. Tune mcq_fate on `MCQ_F*` fair slice to close gap vs LM logprob  
3. Per-question context bundles in single `valhalla_base` batch (reduce LM reload)  
4. Real-modality bake at full 107 scale (TTS + SD pipeline)  
5. Optional guided base — deferred; baked HF + fused LM sufficient for MVP  

---

## 7. Legal

Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved.  
**NOT OPEN SOURCE.** See [NON_OPEN_SOURCE.md](../NON_OPEN_SOURCE.md) and [LICENSE](../LICENSE).

Evaluation and commercial licensing: **licensing@rogue-intelligence.com**
