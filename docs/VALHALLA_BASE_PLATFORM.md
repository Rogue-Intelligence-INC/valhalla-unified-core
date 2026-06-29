# Valhalla Base Platform — 完整技术文档

> **Version:** 2.1 · **Date:** 2026-06-30  
> **Status:** Production documentation · Proprietary — NOT open source  
> **Primary protocol:** `valhalla-base-v1`  
> **Product line:** Valhalla Unified Core (VUC)

---

## 中文概述

Valhalla Unified Core 将 AI 推理栈拆成两层：

1. **结构基座（ValhallaBase）** — 上下文语料经 Triad（Hub / Tile / StemCell / Fate）孵化成可持久化的结构快照；context 可增量追加、可 multimodal ingress，**不依赖 prompt 窗口**。
2. **Decode 头（可选 LM）** — Qwen2.5 等 small LM 作为 runtime patch / logprob 头；开放题默认走 **native 结构检索**，MCQ 走 **LM logprob**。

相对传统 Transformer「prompt = 全部上下文」：

| 维度 | 传统 LM | ValhallaBase |
|------|---------|--------------|
| Context 载体 | Token 序列 | TriadIncubationSnapshot + corpus memories |
| 换 context | 重发全 prompt | Session append（~64 chars/步 wire） |
| 多轮对话 | 历史拼进 prompt | `question_history` + follow-up-aware 检索 |
| 多模态 | Late fusion | Context/core **非隔离融合**（同 session 脉冲） |
| Fate 四系统 | 无 | quad_cycle ingress + QA 反馈闭环 |

**当前生产推荐栈：**

```python
ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",
    fate_qa_feedback=True,
)
```

---

## 1. Architecture stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application / API                            │
│              JSON stdin/stdout · valhalla_base binary            │
└────────────────────────────┬────────────────────────────────────┘
                             │ valhalla-base-v1
┌────────────────────────────▼────────────────────────────────────┐
│  ValhallaBase — context-flexible inference layer                 │
│  · merge_context / session append / multimodal context_items     │
│  · hybrid decode routing (open vs mcq)                           │
│  · follow-up-aware native retrieval                              │
│  · optional core_fusion (task modalities → snapshot)           │
│  · fate_qa_feedback (answer → Fate quality loop)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Native QA    │   │  patch_lm     │   │  mcq_fate     │
│  (Tier B)     │   │  (Qwen decode)│   │  (structure)  │
│  corpus mem   │   │  runtime patch│   │  optional     │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        └─────────┬─────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Triad body — Hub + Tile + StemCell + Fate                       │
│  · signal_ingress: grinder / dl_front → body ports               │
│  · incubation → TriadIncubationSnapshot (fork per QA)            │
│  · Hub quads: BlackHole / MeshBrain / MultiNova / BaseForce      │
└────────────────────────────┬────────────────────────────────────┘
                             │ bake (optional)
┌────────────────────────────▼────────────────────────────────────┐
│  HF export — valhalla-unified-core-v1 baked weights              │
│  patch_vector · quad_layer_scales · valhalla_manifest.json       │
└─────────────────────────────────────────────────────────────────┘
```

**Key idea:** Structure is incubated **before** LM generate. LM reads a **patched snapshot**, not raw RAG text blocks alone.

---

## 2. ValhallaBase — the new model base

### 2.1 Protocol

| Field | Value |
|-------|-------|
| Protocol ID | `valhalla-base-v1` |
| Binary | `valhalla_base` (`hub-f64`) |
| API | JSON request → JSON response (stdin/stdout) |
| Python wrapper | `tools/valhalla_inference/valhalla_base.py` |

### 2.2 Request model

```json
{
  "context": ["line1", "line2"],
  "context_items": [
    {"text": "..."},
    {"audio_features": [0.1, ...]},
    {"image_features": [0.2, ...]}
  ],
  "append_lines": ["new fact"],
  "append_items": [{"text": "incremental"}],
  "session": { "corpus": [], "fingerprint": "...", "snapshot": {} },
  "questions": [
    {
      "id": "q1",
      "text": "What is ...?",
      "score_type": "open",
      "reference_answer": "hint",
      "keywords": ["hint"]
    }
  ],
  "config": {
    "decode": "hybrid",
    "follow_up_decode": "native_follow_up_aware",
    "fate_ingress_routing": "quad_cycle",
    "fate_qa_feedback": true,
    "incubation_cycles": 2,
    "lm_model": "Qwen/Qwen2.5-0.5B-Instruct",
    "strength": 0.08
  }
}
```

### 2.3 Response model

```json
{
  "protocol": "valhalla-base-v1",
  "context_lines": 16,
  "context_fingerprint": "a1b2c3...",
  "decode": "Hybrid",
  "session": {
    "corpus": ["..."],
    "fingerprint": "...",
    "snapshot": { "hub_prefs": [0.31, 0.21, 0.23, 0.25], "hub_routed": [400,400,400,400] },
    "question_history": ["prior Q1"]
  },
  "features": ["context_flex", "hybrid_routing", "fate_ingress_quad_cycle", "fate_qa_feedback"],
  "fate_telemetry": {
    "hub_prefs": [0.31, 0.21, 0.23, 0.25],
    "hub_prefs_spread": 0.10,
    "hub_routed": [400, 400, 400, 400]
  },
  "rows": [
    {
      "id": "q1",
      "answer": "...",
      "decode_path": "valhalla_base/native/...",
      "correct": true,
      "score_type": "open"
    }
  ]
}
```

### 2.4 LM role: decode head, not the base

| Mode | `decode` | Behavior |
|------|----------|----------|
| Structure-only | `native` | Corpus memory retrieval + Tile/Stem alignment; no HF |
| LM patch | `lm_patch` | Snapshot → runtime weight surgery → generate |
| **Production** | **`hybrid`** | `open` → native; `mcq`/`numeric` → LM logprob |

Valhalla **is** the base; LM is optional head. Native path works without GPU HF load.

---

## 3. Context flexibility (maximum product goal)

> Detail: [CONTEXT_FLEXIBILITY_MAX_GOAL.md](./CONTEXT_FLEXIBILITY_MAX_GOAL.md)

### 3.1 Three dimensions

| # | Goal | Mechanism |
|---|------|-----------|
| 1 | **Context growth** | Persistent `session` + `append_lines` / `append_items` |
| 2 | **Topic continuity** | `question_history` + `follow_up_retrieval_boost()` |
| 3 | **Multi-Q disambiguation** | Batch questions on shared incubated snapshot |

### 3.2 Measured results

| Test | Best config | Result |
|------|-------------|--------|
| Context growth (12 appends) | Session append | 16 lines / 638 chars internal; **~64 chars/step** wire |
| Extended threads (30 turns) | `native_follow_up_aware` | **29/30 (96.7%)** vs traditional LM **24/30 (80%)** |
| Multi-Q (9 mixed) | native / follow_up_aware | **9/9** |

### 3.3 Follow-up decode modes

| `follow_up_decode` | Use when |
|--------------------|----------|
| **`native_follow_up_aware`** ✅ | Dialogue sessions — production default |
| `inherit` | Single-shot; no prior-turn boost |
| `lm_patch_on_follow_up` | ⚠️ Not alone — 63.3% on 30-turn test without explicit corpus in prompt |

### 3.4 Native follow-up retrieval

Implemented in `native_qa.rs`:

- Boost keywords from **current** question
- Penalize lines that only match **prior** questions
- Recency bias on `corpus_idx`

Session stores `question_history` across `valhalla_base` calls.

---

## 4. Context × core fusion

> Protocol: `context-core-fusion-v2`

Two-layer incubation before decode:

```
Layer 1 — Context
  corpus lines + multimodal context_items
  → TriadIncubationSnapshot (context bundle)

Layer 2 — Core fusion (optional: core_fusion=true)
  task text + TTS + image pulses in SAME session
  → fuse_universal_core_on_snapshot()
  → tighter cross-modal patch before LM/native decode

Layer 3 — Decode
  hybrid QA on fused snapshot
```

### 4.1 Universal core: isolated vs non-isolated

| Layout | Method | Shared patch (12 tasks) | Universal score (107 tasks) |
|--------|--------|---------------------------|----------------------------|
| Isolated | Separate sessions per modality | ~0.85 | 0.943 avg |
| **Non-isolated** ✅ | One session, interleaved pulses | **~1.00** | **0.964 avg** |

Non-isolated wins **107/107** fair-benchmark tasks.

Real modalities (espeak TTS + SD-Turbo): non-isolated gain **+0.11** vs hash proxies **+0.01** — fusion matters most when channels are genuinely different.

### 4.2 Core fusion QA impact (baseline vs fused)

Report: `reports/context_core_fusion.json` · protocol `context-core-fusion-v2`

| Scope | Baseline (`core_fusion=false`) | Fused (`core_fusion=true`) | Δ |
|-------|-------------------------------|----------------------------|---|
| All 12 tasks | 8/12 (66.7%) | **9/12 (75.0%)** | +8.3pp |
| **MCQ only (5)** | **2/5 (40%)** | **3/5 (60%)** | **+20pp** |
| Open (7) | 6/7 | 6/7 | 0 |

**Per-MCQ (multimodal context — text + TTS + image ingress on both arms):**

| ID | Baseline | Fused | Note |
|----|----------|-------|------|
| MCQ_BIO_01 | A ✗ | **C ✓** | **Only flip** — mitochondria vs chloroplast confusion |
| MCQ_GEO_01 | C ✓ | C ✓ | Already correct |
| MCQ_ECON_01 | A ✗ | A ✗ | LM supply-law prior dominates |
| MCQ_PHIL_01 | B ✓ | B ✓ | Already correct |
| MCQ_MED_01 | A ✗ | A ✗ | Vit A/C confusion; patch nudge insufficient |

**Why fusion helps narrowly (not a general MCQ booster):**

1. **Multimodal without fusion can regress** — same BIO question is **correct** in 46-Q text-only scale test (`scale_benchmark_test.json`, no audio/image) but **wrong (A)** with multimodal context baseline. Fusion realigns patch → fixes that regression.
2. **Structural score ≠ MCQ accuracy** — non-isolated universal_score wins 107/107 and +0.10 on all 5 MCQ tasks, yet only BIO crosses the logprob threshold.
3. **Baked weights already encode fusion** — `base_load_fused_crossmodal12.json` MCQ **3/5 (60%)** matches runtime `core_fusion=true`; runtime baseline **2/5** is the gap fusion closes.
4. **46-Q fusion ablation not yet run** — current 63% MCQ is text-only, `core_fusion=false`. Expect at most ~+2–4 questions if multimodal sessions are common.

Enable: `config.core_fusion=true` when task carries `audio_features` / `image_features` (no-op on text-only tasks).

---

## 5. Fate layer — ingress, weights, QA feedback

> Ingress detail: [FATE_INGRESS_ROUTING.md](./FATE_INGRESS_ROUTING.md)

### 5.1 Hub four quads

| Quad | Role | Semantic bucket |
|------|------|-----------------|
| BlackHole | Force / gravity field | physics, energy, newton |
| MeshBrain | Language mesh | text, language, symbols |
| MultiNova | Process evolution | chemistry, phase, reaction |
| BaseForce | Spatial coordination | geography, capitals |

Tile and StemCell **always** receive full port batches. Hub routing affects Fate meta-learning only.

### 5.2 Ingress routing (production: `quad_cycle`)

Each corpus line → 32 Hub signals → **8 per quad (25% each)** within the line loop.

| Mode | 4-quad activation | Accuracy (15+15) | Fate spread |
|------|-------------------|------------------|-------------|
| **`quad_cycle`** ✅ | 4/4 balance=1.0 | **93.3%** P1 | 0 (symmetric ingress) |
| semantic | 2/4 dominant ~60% | 91.1% | ~0.93 |
| hybrid_quad_semantic | 4/4 balance=0.75 | 91.1% | ~0.88 |

**Why quad_cycle:** Best accuracy + guaranteed four-system activation per ingest loop.

### 5.3 QA → Fate feedback loop (v2)

**Problem:** Fate weights stayed uniform under quad_cycle — no task-driven learning.

**Solution:** `fate_qa_feedback=true` (default):

After each answer:
1. Semantic-primary quad (from question text) gets **high quality** if correct, **low** if wrong
2. Other quads get proportional signal
3. Tile/Stem `triple_fate.receive_passive()` pulsed
4. Updated snapshot persisted in session

**40-round test** (20 gradual constraint + 20 free):

| Phase | Accuracy | spread |
|-------|----------|--------|
| Gradual (constraint 1.0→0.05) | **86.7%** | 0.089 |
| Free (routing free, evaluated) | 68.3% | 0.125 |

Fate prefs after 40 rounds (ingress still 25% each, **prefs learned**):

```
physics:   BH 31.4% | MB 21.2% | MN 22.9% | BF 24.5%
chemistry: BH 20.7% | MB 22.7% | MN 35.8% | BF 20.7%
australia: BH 21.1% | MB 22.4% | MN 21.1% | BF 35.5%
```

Report: `reports/fate_qa_feedback_40.json`

### 5.4 Constraint ladder (known pitfall)

Medium constraint (topic-only append, no answer keywords) scored **11%** in 4-tier ladder test — **U-curve**. Production: avoid half-released constraint tiers; use full session append or full release.

---

## 6. Hybrid decode routing

```
score_type ──┬── open ──────────► native retrieval (corpus memories)
             │                      + follow_up_retrieval_boost
             │
             ├── mcq / numeric ───► LM logprob (default)
             │                      or structure mcq_fate (optional)
             │
             └── hybrid config ───► routes per question automatically
```

| Slice | Hybrid LM | Structure mcq_fate |
|-------|-----------|-------------------|
| Open retrieval (31) | native **97%** | N/A |
| MCQ (46) | **63%** | 35% |

---

## 7. Bake & HF model export

Protocol: `valhalla-unified-core-v1`

```
Fair corpus + multimodal samples
  → non-isolated Triad incubation
  → bake_valhalla_model
  → models/hf/Qwen2.5-0.5B-Unified-Core-v1-*/
      ├── model.safetensors
      ├── valhalla_manifest.json
      └── hf_export.json
```

Product tag in manifest ties baked weights to VUC protocol version. Runtime can:

- Load baked weights only (no live surgery), or
- Apply runtime patch per context bundle via `patch_lm`

Cross-modal12 bake report: `reports/bake_crossmodal12.json`

---

## 8. Production configuration reference

### 8.1 Python (recommended)

```python
from valhalla_base import ValhallaBase

base = ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",
    fate_qa_feedback=True,
    fate_weight_mode="fixed",       # high-constraint explore phase
    fate_routing_free=False,        # lock routing during context build
    incubation_cycles=2,
    lm_model="Qwen/Qwen2.5-0.5B-Instruct",
    strength=0.08,
)

base.set_context(["Fact line 1", "Fact line 2"])
doc = base.run([{"id": "q1", "text": "Question?", "score_type": "open",
                 "reference_answer": "hint", "keywords": ["hint"]}])
base.append_context("New fact from turn 2")
doc2 = base.run([{"id": "q2", "text": "Follow-up?", "score_type": "open",
                  "reference_answer": "hint2", "keywords": ["hint2"]}],
                append_only=True)
```

### 8.2 Release phase (after context stable)

```python
base.fate_weight_mode = "evaluated"
base.fate_routing_free = True
base.incubation_cycles = 4  # avoid 15 — reduces Tile/Stem drift
```

### 8.3 Build

```bash
cd /path/to/Valhalla
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release \
  --bin valhalla_base --bin valhalla_universal_core
```

---

## 9. Benchmark index

| Report | Test | Key metric |
|--------|------|------------|
| `context_flexibility_max_goal.json` | 30-turn extended threads | 96.7% follow_up_aware |
| `fate_weight_ladder_compare_30.json` | Ingress mode compare (3 modes) | 93.3% quad_cycle P1 |
| `fate_qa_feedback_40.json` | QA→Fate 20+20 | prefs differentiate by topic |
| `context_core_fusion.json` | Baseline vs core_fusion (12 tasks) | MCQ 40%→60% |
| `scale_benchmark_test.json` | 107-task scale (46 MCQ text-only) | MCQ 63% · open 97% |
| `base_load_fused_crossmodal12.json` | Baked fused LM load | MCQ 3/5 |
| `cross_modal_test_summary.json` | 12-task tri-modal | non-iso patch ~1.0 |
| `bake_crossmodal12.json` | HF bake smoke | export validation |
| `qa_smoke_summary.json` | Baked model QA | post-bake inference |

Monorepo mirror: `Valhalla/reports/valhalla_inference/`

---

## 10. Reproduce commands

```bash
# Context flexibility max goal
python3 tools/valhalla_inference/test_context_flexibility_goal.py

# Context architecture compare (native vs LM prompt)
python3 tools/valhalla_inference/test_context_arch_compare.py

# Deep flexibility (growth, threads, multi-Q)
python3 tools/valhalla_inference/test_context_flexibility_deep.py

# Constraint ladder (4 tiers)
python3 tools/valhalla_inference/test_context_constraint_ladder.py

# Fate ingress modes
python3 tools/valhalla_inference/test_fate_weight_ladder_200.py --compare-all

# QA → Fate feedback
python3 tools/valhalla_inference/test_fate_qa_feedback_40.py

# E7 algebra + corpus line affinity + FOG
python3 tools/valhalla_inference/test_fate_algebra_corpus_v1.py

# Long session memory (4 arms)
python3 tools/valhalla_inference/test_long_memory_v1.py

# Proactive idle + FOG nudge
python3 tools/valhalla_inference/test_proactive_fate_v2.py

# Context × core fusion
python3 tools/valhalla_inference/test_context_core_fusion.py --limit 12

# VUC scripts (this repo)
python3 scripts/run_cross_modal.py --phase test --limit 12
python3 scripts/run_bake.py --phase smoke --strong
python3 scripts/run_qa.py --phase smoke
```

---

## 11. Code map (Valhalla monorepo)

| Component | Path |
|-----------|------|
| E7 algebra (τ, Δ, affinity) | `manifestsys/hub-f64/src/e7_algebra.rs` |
| ValhallaBase API | `manifestsys/hub-f64/src/valhalla_base.rs` |
| Native QA + follow-up boost | `manifestsys/hub-f64/src/native_qa.rs` |
| Signal ingress + snapshot | `manifestsys/hub-f64/src/signal_ingress.rs` |
| Hub Fate + ingress routing | `manifestsys/hub-f64/src/lib.rs` |
| Core fusion | `manifestsys/hub-f64/src/free_multimodal_fate.rs` |
| LM patch decode | `manifestsys/hub-f64/src/patch_lm.rs` |
| Python API | `tools/valhalla_inference/valhalla_base.py` |
| Fate system | `systems/metasystems/fate-f64/` |

---

## 12. Document index

| Doc | Topic |
|-----|-------|
| [INTRODUCTION.md](./INTRODUCTION.md) | Product intro & investor-facing summary |
| [FATE_E7_ALGEBRA_AND_MEMORY.md](./FATE_E7_ALGEBRA_AND_MEMORY.md) | E7 algebra · line affinity · long memory · proactive v2 |
| **This document** | Full platform: base + context + fusion + Fate |
| [CONTEXT_FLEXIBILITY_MAX_GOAL.md](./CONTEXT_FLEXIBILITY_MAX_GOAL.md) | Context flexibility goal & 30-turn results |
| [FATE_INGRESS_ROUTING.md](./FATE_INGRESS_ROUTING.md) | Quad ingress experiments |
| [../PROTOCOL.md](../PROTOCOL.md) | Universal core bake protocol |

---

## 13. Roadmap (priority order)

1. **46×2 MCQ ablation** — `run_scale_benchmark.py` with `core_fusion=true` + multimodal samples; quantify fusion on full fair MCQ slice
2. **LM prior fixes for ECON/MED-class errors** — corpus-aware logprob compose or stronger patch strength on mcq_fate fallback items
3. **Retrieval ↔ Fate coupling** — increase `hub_prefs` weight in `score_memories` (currently ~0.02 logprob bias)
4. **DeformationSignal direction** — pass corpus embedding, not `vec![0.0;4]`
5. **Free-phase stability** — cap `incubation_cycles` on release; fix −13~−18pp constraint-release drop
6. **Real-modality bake @ 107 scale** — TTS + SD full pipeline export (runtime fusion ≈ bake for BIO-class fixes)
7. **Per-batch snapshot reuse** — single LM load for multi-question session

---

## 14. Legal

Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved.  
**NOT OPEN SOURCE.** See [NON_OPEN_SOURCE.md](../NON_OPEN_SOURCE.md).

Commercial licensing: **licensing@rogue-intelligence.com**
