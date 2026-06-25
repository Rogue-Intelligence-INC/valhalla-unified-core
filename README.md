# Valhalla Unified Core (VUC)

> **NOT OPEN SOURCE** — Proprietary asset of Rogue Intelligence LNC.  
> See [**NON_OPEN_SOURCE.md**](./NON_OPEN_SOURCE.md) · [LICENSE](./LICENSE)

**One session. One core. Text, speech, and image — fused before decode.**

| | |
|--|--|
| **Product** | Valhalla Unified Core (VUC) |
| **Protocols** | `valhalla-unified-core-v1` · `valhalla-base-v1` · `context-core-fusion-v2` |
| **Runtime** | [Valhalla monorepo](https://github.com/Rogue-Intelligence-INC/Valhalla) (`hub-f64`, proprietary) |
| **License** | **Proprietary — NOT open source** |
| **Intro page** | [page/index.html](./page/index.html) (open locally in a browser) |
| **Detailed docs** | [docs/INTRODUCTION.md](./docs/INTRODUCTION.md) |

---

## What it is

Valhalla Unified Core is Rogue Intelligence’s **multimodal structure substrate** for AI that does not treat text, TTS, and image as three disconnected forward passes.

Instead, VUC runs **non-isolated concurrent fusion** inside a single Triad session (Hub / Tile / StemCell / Fate): the same task is pulsed through text, audio, and image channels in one incubation loop, forming a **universal core** that tightens cross-modal patch alignment before any LM decode.

On top of that substrate sits **ValhallaBase** — a context-flexible inference layer with:

- **Hybrid routing** — open questions → native corpus retrieval; MCQ → LM logprob or structure `mcq_fate`
- **Persistent session** — incremental context append without full re-ingest
- **Multimodal context** — text / audio features / image features in one context bundle
- **Core fusion** — fuse task modalities into the context snapshot before structure→LM decode
- **Follow-up-aware context** — session `question_history` + corpus ranking that penalizes prior-turn sticky retrieval ([max goal doc](./docs/CONTEXT_FLEXIBILITY_MAX_GOAL.md))
- **Fate ingress routing** — **`quad_cycle` (production default)**: each corpus line evenly activates all four Hub quads (25% each); see [Fate ingress summary](./docs/FATE_INGRESS_ROUTING.md)

---

## Fate ingress routing (production default: `quad_cycle`)

When Fate routing is locked (`fate_routing_free=false`), Hub distributes each corpus line's signals evenly across **BlackHole / MeshBrain / MultiNova / BaseForce** (8 signals per quad per line). This maximizes four-system activation and gave the best accuracy in our 15+15 × 3-thread compare (**93.3% Phase1**, **80.0% Phase2**).

| Mode | Phase1 | Four-quad balance | Fate spread |
|------|--------|-------------------|-------------|
| **`quad_cycle`** ✅ | **93.3%** | **1.00** (25% each) | 0 (symmetric) |
| semantic | 91.1% | 0.51 (one quad ~60%) | ~0.93 |
| hybrid_quad_semantic | 91.1% | 0.75 | ~0.88 |

Full experiment write-up: **[docs/FATE_INGRESS_ROUTING.md](./docs/FATE_INGRESS_ROUTING.md)** · reports in `reports/fate_weight_ladder_*.json`

```python
ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",  # default
)
```

---

## Maximum goal: context flexibility

See **[docs/CONTEXT_FLEXIBILITY_MAX_GOAL.md](./docs/CONTEXT_FLEXIBILITY_MAX_GOAL.md)** — one of VUC's primary product targets.

| Dimension | Best architecture | Result |
|-----------|-------------------|--------|
| Context growth (12 appends) | ValhallaBase session | 16 lines / 638 chars internal; ~64 chars/step wire |
| Extended topic continuity (30 turns) | **follow_up_aware native** | **29/30 (96.7%)** vs traditional 24/30 (80%) |
| Multi-Q disambiguation (9 Q) | native / follow_up_aware / trad | **9/9** |

---

## Measured results (fair test phase)

| Capability | Scale | Result |
|------------|-------|--------|
| Universal core (non-isolated vs isolated) | 107 tasks | **107/107** non-isolated wins; avg universal score **0.964** vs **0.943** |
| Cross-modal shared patch (12 tasks) | compare | non-isolated **~1.00** vs isolated **~0.85** |
| Real TTS + SD-turbo modalities | 12 tasks | core forms **12/12**; larger fusion gain vs hash proxies |
| Open retrieval (targeted context) | 31 tasks | **30/31 (97%)** native retrieval |
| Context swap / session | 3 pairs + 12 appends | **3/3** swap correct; fingerprint tracks append |
| MCQ (hybrid LM logprob) | 46 tasks | **63%** (structure-only mcq_fate **35%** at current tuning) |

Full reports live in the Valhalla monorepo under `reports/valhalla_inference/` and in this repo’s `reports/`.

---

## Repository layout

```
valhalla-unified-core/
├── PROTOCOL.md              Core fusion protocol (non-isolated bake)
├── docs/
│   ├── INTRODUCTION.md      Detailed English product & architecture guide
│   ├── CONTEXT_FLEXIBILITY_MAX_GOAL.md
│   └── FATE_INGRESS_ROUTING.md   Quad ingress modes & production default
├── page/
│   └── index.html           Public-style introduction landing page
├── scripts/
│   ├── run_cross_modal.py   Same-task text / TTS / image compare
│   ├── run_experiment.py    Universal-core smoke / test
│   ├── run_bake.py          HF bake pipeline
│   └── run_qa.py              QA on baked model
├── reports/                 Experiment JSON (cross-modal, QA, bake)
├── fixtures/                Benchmark fixtures
└── models/hf/               Baked HF exports (weights gitignored)
```

Runtime binaries (`valhalla_universal_core`, `valhalla_base`) are built from the Valhalla monorepo:

```bash
cd /path/to/Valhalla
RUSTFLAGS='-L /opt/cuda/lib64' cargo build -p hub-f64 --release \
  --bin valhalla_universal_core --bin valhalla_base
```

---

## Quick start (requires Valhalla monorepo checkout)

```bash
# Cross-modal: same question via text, TTS, image — isolated vs non-isolated
python3 scripts/run_cross_modal.py --phase test --limit 12

# Structure-only universal core experiment
python3 scripts/run_experiment.py --phase smoke --limit 4

# Bake fused weights → models/hf/
python3 scripts/run_bake.py --phase smoke --strong

# QA on baked HF model
python3 scripts/run_qa.py --phase smoke
```

Scale & context benchmarks (monorepo):

```bash
python3 tools/valhalla_inference/run_scale_benchmark.py --phase test --skip-mcq
python3 tools/valhalla_inference/test_context_core_fusion.py --limit 12
python3 tools/valhalla_inference/run_real_modality_core_compare.py --limit 12
```

---

## Protocol IDs

| Protocol | Purpose |
|----------|---------|
| `valhalla-universal-core-v1` | Isolated vs non-isolated same-task tri-modal metrics |
| `valhalla-unified-core-v1` | **Production** non-isolated bake + HF export |
| `valhalla-base-v1` | Context-flexible substrate + optional LM decode head |
| `context-core-fusion-v2` | Context bundle + universal core + hybrid QA pipeline |

---

## Private repository

This tree is intended as a **standalone private repo**:

```bash
cd valhalla-unified-core
git init
git add .
git commit -m "Initial Valhalla Unified Core product repo"
gh repo create Rogue-Intelligence-INC/valhalla-unified-core --private --source=. --push
```

---

## Contact

**Rogue Intelligence LNC.**  
Licensing & evaluation: **licensing@rogue-intelligence.com**

---

*Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved.*
