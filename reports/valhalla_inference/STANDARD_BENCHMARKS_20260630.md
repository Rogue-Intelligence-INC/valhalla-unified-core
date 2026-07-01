# Standard third-party benchmarks — 2026-06-30

ValhallaBase on **recognized external benchmarks** + industry extensions.

**Valid interpretation (runs · meaning · because):** [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](VALID_BENCHMARKS_INTERPRETATION_20260630.md)  
**Industry report:** [`INDUSTRY_BENCHMARKS_20260630.md`](INDUSTRY_BENCHMARKS_20260630.md)  
**Master summary:** [`EXPERIMENT_SUMMARY_20260630.md`](EXPERIMENT_SUMMARY_20260630.md)

---

## Results (2026-06-30 · robust download + full run)

| Benchmark | Valid | Runs | n | Result | Verdict |
|-----------|-------|------|---|--------|---------|
| **RAGTruth** | A | ×2 | 40 | **40/40 (100%)** | RAGTRUTH_STRONG |
| **RAGTruth-100** | A | ×1 | 100 | **100/100 (100%)** | RAGTRUTH_STRONG |
| **Needle session** | A | ×2 | 4 | **4/4 (100%)** | NEEDLE_STRONG |
| **RULER-style** | A | ×1 | 20 | **20/20 (100%)** | NEEDLE_STRONG |
| **External holdout** | A | ×1 | 15 | **15/15 (100%)** | EXTERNAL_HOLDOUT_STRONG |
| **MCQ ladder** | A | ×1 | 46 | **65% → 98%** | MCQ_LADDER_SCALES |
| **MultiHop-RAG** | B | ×1 | 25 | **9/25 (36%)** | OPEN_QA_DEVELOPING |
| **LongBench-v2** | B | ×1 | 20 | **7/20 (35%)** | LONGBENCH_V2_VIABLE |
| **LaRA RAG vs LC** | B | ×1 | 20 | RAG 25% · LC 70% | STRUCTURE_RAG_BELOW_LC |
| **LoCoMo** | B† | ×1 | 30 | **1/30 (3%)** | OPEN_QA_DEVELOPING |
| **FRAMES** | C | — | 25 | 0/25 | FRAMES_NEEDS_WIKI |

---

## Tier A highlights

| Benchmark | Meaning | Because |
|-----------|---------|---------|
| RAGTruth | RAG faithfulness industry-strong | ingest + Fate retrieval + FOG abstain |
| Needle/RULER | Session recall to 62+ lines | structural index, not 128K window |
| MCQ ladder | lm_patch scales with Qwen size | sharded Rust Candle + hybrid logprob |
| Holdout | Out-of-suite generalization | no benchmark overfitting |

See full table in [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](VALID_BENCHMARKS_INTERPRETATION_20260630.md).

---

*Rogue Intelligence LNC.*
