# Valhalla Unified Core (VUC)

> **NOT OPEN SOURCE** — Proprietary asset of Rogue Intelligence LNC.  
> See [**NON_OPEN_SOURCE.md**](./NON_OPEN_SOURCE.md) · [LICENSE](./LICENSE)

**Valhalla is the base. The LM is the decode head.**

One Triad session · persistent context · multimodal fusion · structure-first inference.

| | |
|--|--|
| **Product** | Valhalla Unified Core (VUC) |
| **Model base** | **ValhallaBase** (`valhalla-base-v1`) |
| **Protocols** | `valhalla-base-v1` · `valhalla-unified-core-v1` · `context-core-fusion-v2` |
| **Runtime** | [Valhalla monorepo](https://github.com/Rogue-Intelligence-INC/Valhalla) (`hub-f64`, proprietary) |
| **Full documentation** | **[docs/EN_ENGINEERING_WHITEPAPER.md](./docs/EN_ENGINEERING_WHITEPAPER.md)** · [Platform](./docs/VALHALLA_BASE_PLATFORM.md) |
| **Intro page** | [page/index.html](./page/index.html) |

---

## What makes this different

Traditional LLMs pack all context into a prompt window. **ValhallaBase** incubates context into a **Triad structure snapshot** (Hub / Tile / StemCell / Fate), then decodes:

| | Transformer prompt stack | ValhallaBase |
|--|--------------------------|--------------|
| Context | Tokens in window | Corpus → structure snapshot |
| Multi-turn | Resend full history | Session append (~64 chars/step) |
| Multimodal | Late encoder fusion | **Non-isolated core fusion** in one session |
| Open questions | Generate from weights | **Native corpus retrieval** (97% @ 31 tasks) |
| MCQ | Same generate path | Hybrid → LM logprob (**63%** @ 46 tasks) |
| Four-system body | N/A | Fate quad ingress + QA feedback loop |

---

## Production stack (2026-06)

```python
from valhalla_base import ValhallaBase

base = ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",
    fate_qa_feedback=True,
)
base.set_context(["Your corpus lines…"])
base.run(questions)
base.append_context("Incremental fact")   # session grows without full re-send
base.run(follow_up_questions, append_only=True)
```

| Knob | Production value | Why |
|------|------------------|-----|
| `decode` | `hybrid` | open → native; mcq → LM |
| `follow_up_decode` | `native_follow_up_aware` | **96.7%** on 30-turn threads |
| `fate_ingress_routing` | `quad_cycle` | 4/4 Hub quads active every ingest |
| `fate_qa_feedback` | `true` | Answer → Fate learns topic prefs + **E7 line affinity** |

**2026-06-30:** E7 algebra module (`e7_algebra.rs`) · long-memory **96%** · proactive v2 **100%** — see [FATE_E7_ALGEBRA_AND_MEMORY.md](./docs/FATE_E7_ALGEBRA_AND_MEMORY.md)

---

## Headline results (Tier A — cite externally)

| Highlight | Result |
|-----------|--------|
| **RAGTruth** (ACL 2024) | **100/100** context-grounded · 0 abstain |
| **Needle + RULER** | **4/4 · 20/20** session recall |
| **External holdout** | **15/15** |
| **MCQ ladder** (46Q, Qwen lm_patch) | **65% → 98%** (0.5B → 3B) |
| **Long memory** | **73/76 (96.0%)** |
| **Follow-up native** (30-turn) | **96.7%** |
| **Proactive Fate v2** | **72/72 · PPI 0.921** |
| **Open retrieval** (targeted) | **31/31 (100%)** |

**Interpretation:** [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](./reports/valhalla_inference/VALID_BENCHMARKS_INTERPRETATION_20260630.md) · [`EXPERIMENT_SUMMARY_20260630.md`](./reports/valhalla_inference/EXPERIMENT_SUMMARY_20260630.md)

<details>
<summary>Extended internal metrics</summary>

| Capability | Result |
|------------|--------|
| **Zero cross-topic hallucination** | **0/48** drift probes |
| **Context swap fidelity** | **12/12 (100%)** |
| **E7 algebra + Fate corpus** | Rust τ/Δ ↔ Python |
| **Universal core** (107 tasks) | **107/107** vs isolated |
| **Cross-modal fusion** (12 tasks) | Non-isolated **~1.00** vs **~0.85** |
| **Core fusion QA** (12 tasks) | **75%** vs **66.7%** |
| **MCQ hybrid** (46 tasks, 0.5B) | **63%** LM logprob |
| **LongBench-v2** (short, trunc) | **7/20 (35%)** |
| **Scaling open** @ 0.5B vs trad | **100%** · **+6.5pp** |
| **0→1 transfer** (no LM SGD) | **87.1%** fresh |

</details>

Scaling: [`MODEL_SCALING_20260630.md`](./reports/valhalla_inference/MODEL_SCALING_20260630.md) · MCQ ladder: [`MCQ_LADDER_20260630.md`](./reports/valhalla_inference/MCQ_LADDER_20260630.md)

Reports in [`reports/`](./reports/) · **Engineering pack:** [Whitepaper](./docs/EN_ENGINEERING_WHITEPAPER.md) · [BP](./docs/EN_ENGINEERING_BUSINESS_PLAN.md) · [DD](./docs/EN_ENGINEERING_DUE_DILIGENCE.md)

---

## Architecture (one glance)

```
Context (text / audio / image)
        │
        ▼
┌───────────────────────────────────┐
│  ValhallaBase — context flex       │
│  session · append · multimodal       │
│  quad_cycle ingress · QA→Fate      │
└───────────────┬───────────────────┘
                ▼
┌───────────────────────────────────┐
│  Triad — Hub · Tile · Stem · Fate  │
│  TriadIncubationSnapshot           │
└───────────────┬───────────────────┘
                ▼
     ┌──────────┴──────────┐
     ▼                     ▼
 Native retrieval      LM patch (Qwen)
 (open questions)      (MCQ logprob)
```

Optional **core fusion** fuses task modalities into the snapshot before decode.  
Optional **HF bake** exports structure into `models/hf/` (`valhalla-unified-core-v1`).

---

## Documentation

| Document | Description |
|----------|-------------|
| **[VALHALLA_BASE_PLATFORM.md](./docs/VALHALLA_BASE_PLATFORM.md)** | Complete platform doc — base, context, fusion, Fate |
| **[EN_ENGINEERING_WHITEPAPER.md](./docs/EN_ENGINEERING_WHITEPAPER.md)** | Engineering whitepaper (architecture & benchmarks) |
| **[EN_ENGINEERING_BUSINESS_PLAN.md](./docs/EN_ENGINEERING_BUSINESS_PLAN.md)** | Engineering business plan (GTM & KPIs) |
| **[EN_ENGINEERING_DUE_DILIGENCE.md](./docs/EN_ENGINEERING_DUE_DILIGENCE.md)** | Due diligence pack (claims matrix & risks) |
| [CONTEXT_FLEXIBILITY_MAX_GOAL.md](./docs/CONTEXT_FLEXIBILITY_MAX_GOAL.md) | Context flexibility product goal |
| [FATE_INGRESS_ROUTING.md](./docs/FATE_INGRESS_ROUTING.md) | Quad ingress modes & benchmarks |
| [INTRODUCTION.md](./docs/INTRODUCTION.md) | Product introduction |
| [PROTOCOL.md](./PROTOCOL.md) | Universal core bake protocol |

---

## Quick start

**Build** (requires Valhalla monorepo):

```bash
cd /path/to/Valhalla
RUSTFLAGS='-L /opt/cuda/lib64' cargo build -p hub-f64 --release \
  --bin valhalla_base --bin valhalla_universal_core
```

**This repo scripts:**

```bash
python3 scripts/run_cross_modal.py --phase test --limit 12
python3 scripts/run_bake.py --phase smoke --strong
python3 scripts/run_qa.py --phase smoke
```

**Monorepo benchmarks:**

```bash
python3 tools/valhalla_inference/test_context_flexibility_goal.py
python3 tools/valhalla_inference/test_fate_qa_feedback_40.py
python3 tools/valhalla_inference/test_context_core_fusion.py --limit 12
```

---

## Repository layout

```
valhalla-unified-core/
├── docs/
│   ├── VALHALLA_BASE_PLATFORM.md   ← full technical reference
│   ├── CONTEXT_FLEXIBILITY_MAX_GOAL.md
│   ├── FATE_INGRESS_ROUTING.md
│   └── INTRODUCTION.md
├── reports/                        JSON experiment outputs
├── scripts/                        cross-modal · bake · QA runners
├── models/hf/                      baked HF exports (weights gitignored)
├── page/index.html                 landing page
└── PROTOCOL.md
```

---

## Protocol IDs

| Protocol | Purpose |
|----------|---------|
| `valhalla-base-v1` | Context-flexible base + hybrid decode |
| `valhalla-unified-core-v1` | Non-isolated bake + HF export |
| `context-core-fusion-v2` | Context bundle + core fusion + QA |
| `valhalla-universal-core-v1` | Isolated vs non-isolated metrics |

---

## Contact

**Rogue Intelligence LNC.**  
Licensing & evaluation: **licensing@rogue-intelligence.com**

---

*Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved.*
