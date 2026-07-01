# Industry benchmarks — ValhallaBase

**Generated:** 2026-06-30T23:58:49.854369+00:00  
**Interpretation guide:** [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](VALID_BENCHMARKS_INTERPRETATION_20260630.md)

## Results

| Benchmark | Valid | Runs | Protocol | Result | Verdict |
|-----------|-------|------|----------|--------|---------|
| RAGTruth | A | ×2 | `ragtruth-v1` | **40/40 (100%)** | RAGTRUTH_STRONG |
| RAGTruth-100 | A | ×1 | `ragtruth-full-v1` | **100/100 (100%)** | RAGTRUTH_STRONG |
| Needle session | A | ×2 | `needle-session-v1` | **4/4 (100%)** | NEEDLE_STRONG |
| LongBench-v2 | B | ×1 | `longbench-v2-v1` | **7/20 (35%)** | LONGBENCH_V2_VIABLE |
| FRAMES | C | — | `frames-v1` | 0/25 (no wiki) | FRAMES_NEEDS_WIKI |
| MultiHop-RAG | B | ×1 | `multihop-rag-v1` | **9/25 (36%)** | OPEN_QA_DEVELOPING |
| LoCoMo | B† | ×1 | `locomo-v1` | **1/30 (3%)** | OPEN_QA_DEVELOPING |
| RULER-style | A | ×1 | `ruler-v1` | **20/20 (100%)** | NEEDLE_STRONG |
| LaRA RAG vs LC | B | ×1 | `lara-v1` | **RAG 5/20 · LC 14/20** | STRUCTURE_RAG_BELOW_LC |
| MCQ ladder | A | ×1 | `mcq-ladder-v1` | **0.5B 65% → 3.0B 98%** (46Q) | MCQ_LADDER_SCALES |
| External holdout | A | ×1 | `external-holdout-v1` | **15/15 (100%)** | EXTERNAL_HOLDOUT_STRONG |

## Roadmap (pending)

- U-NIAH multi-needle (extend ruler-v2)
- RAGBench end-to-end (galileo-ai/ragbench)
- FRAMES full 824Q + wiki fetch
- LoCoMo locomo-v2 chunked append (remove 64-line cap)
- Qwen 7B MCQ ladder measured
- RAGAS reference-free on production traces

## Run

```bash
HF_ENDPOINT=https://hf-mirror.com .venv-llm/bin/python3 tools/standard_benchmarks/download_standard_benchmarks.py --all --no-wiki-fetch
RUSTFLAGS="-L /opt/cuda/lib64" python3 tools/valhalla_inference/run_industry_benchmarks.py --all
```

---

*Rogue Intelligence LNC.*
