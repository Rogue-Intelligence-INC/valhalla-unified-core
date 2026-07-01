# Valhalla Unified Core — documentation index

| Document | Description |
|----------|-------------|
| [../README.md](../README.md) | GitHub landing page · quick start · production config |
| **[VALHALLA_BASE_PLATFORM.md](./VALHALLA_BASE_PLATFORM.md)** | Full platform reference (EN/ZH overview) |
| **[EN_ENGINEERING_WHITEPAPER.md](./EN_ENGINEERING_WHITEPAPER.md)** | Engineering whitepaper — architecture & benchmarks |
| **[EN_ENGINEERING_BUSINESS_PLAN.md](./EN_ENGINEERING_BUSINESS_PLAN.md)** | Engineering business plan — GTM & KPIs |
| **[EN_ENGINEERING_DUE_DILIGENCE.md](./EN_ENGINEERING_DUE_DILIGENCE.md)** | Due diligence — claims matrix & risks |
| [INTRODUCTION.md](./INTRODUCTION.md) | Product introduction |
| **[EXPERIMENT_RECORD_INFERENCE_PARADIGM.md](./EXPERIMENT_RECORD_INFERENCE_PARADIGM.md)** | **推理范式实验记录（TPI-v2 / NPPI / 复现）** |
| **[FATE_E7_ALGEBRA_AND_MEMORY.md](./FATE_E7_ALGEBRA_AND_MEMORY.md)** | E7 τ/Δ · line affinity · long-memory · proactive v2 |
| **[FATE_OUTPUT_GATE.md](./FATE_OUTPUT_GATE.md)** | Fate 何时输出（FOG 三道门 + v1 benchmark） |
| [CONTEXT_FLEXIBILITY_MAX_GOAL.md](./CONTEXT_FLEXIBILITY_MAX_GOAL.md) | Context flexibility goal |
| [FATE_INGRESS_ROUTING.md](./FATE_INGRESS_ROUTING.md) | Fate Hub ingress |
| [../PROTOCOL.md](../PROTOCOL.md) | Universal core bake protocol |
| [../NON_OPEN_SOURCE.md](../NON_OPEN_SOURCE.md) | Proprietary declaration |
| [../page/index.html](../page/index.html) | Landing page |

## Key reports (`../reports/`)

| Report | Topic |
|--------|-------|
| `context_topic_drift_test.json` | Swap, distractor, interleave, recency |
| `context_topic_drift_extended_test.json` | 30-turn follow-up drift |
| `valhalla_base_training_potential_test_v2.json` | Training potential v2 (TPI) |
| `new_paradigm_potential_test.json` | New paradigm potential (NPPI) |
| `local_corpus_demo_test.json` | Local markdown corpus ingest demo |
| `scale_benchmark_test.json` | 107 core + 46 MCQ + open |
| `context_core_fusion.json` | Multimodal core fusion QA |
| `valhalla_inference/STEM_TILE_ORGAN_AGGREGATION_ANALYSIS_20260628.md` | Stem organ / Tile merge — mechanism & measured effect |
| `valhalla_inference/BACKBONE_UNIVERSALITY_SUMMARY_20260628.md` | Backbone universality — Gemma / Phi-3 / Qwen trad_lm vs structure hybrid |
| `valhalla_inference/LONG_MEMORY_OPTIMIZATION_20260628.md` | Long memory v1 · structure-first · 73/76 |
| `valhalla_inference/proactive_fate_v2_test.json` | Proactive Fate v2 · 72/72 · PPI 0.921 |
| `valhalla_inference/fate_algebra_corpus_v1.json` | E7 algebra + Fate corpus affinity |
| `valhalla_inference/VALID_BENCHMARKS_INTERPRETATION_20260630.md` | **有效 benchmark 解读 — 次数 · 含义 · 因为什么** |
| `valhalla_inference/valid_benchmarks_summary.json` | Tier A/B/C JSON index |
| `valhalla_inference/STANDARD_BENCHMARKS_20260630.md` | RAGTruth · Needle · LongBench-v2 third-party |
| `valhalla_inference/ragtruth_v1_test.json` | RAGTruth 40/40 context-grounded |
| `valhalla_inference/needle_session_v1_test.json` | Needle recall 4/4 |
| `valhalla_inference/longbench_v2_v1_test.json` | LongBench-v2 short MCQ 7/20 |
| `valhalla_inference/EXPERIMENT_SUMMARY_20260630.md` | Master summary — link to valid interpretation |
| `valhalla_inference/recognized_benchmarks_summary.json` | Aggregated benchmark index |
| `valhalla_inference/model_scaling_v1_test.json` | Scaling ladder JSON (0.5B/2B/3.8B) |
| `valhalla_inference/MCQ_LADDER_20260630.md` | Qwen lm_patch MCQ ladder 0.5B→3B |
| `valhalla_inference/mcq_ladder_v1_test.json` | MCQ ladder JSON · sharded safetensors |

- `manifestsys/hub-f64/src/valhalla_base.rs`
- `tools/valhalla_inference/`
- `reports/valhalla_inference/` — full JSON mirror
