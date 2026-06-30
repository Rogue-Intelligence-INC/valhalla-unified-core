# ValhallaBase — 公认 Benchmark 实验总结

**Generated:** 2026-06-30T03:39:27.966241+00:00

## 总表

| Benchmark | Protocol | n | Result | Verdict |
|-----------|----------|---|--------|---------|
| RAGTruth (ACL 2024) | `ragtruth-v1` | 40 | **40/40 grounded (100%)** | RAGTRUTH_STRONG |
| Needle-in-haystack (session) | `needle-session-v1` | depths [5, 10, 20, 30] | **4/4 recall (100%)** | NEEDLE_STRONG |
| LongBench-v2 (THUDM) | `longbench-v2-v1` | 20 | **7/20 (35%)** | LONGBENCH_V2_VIABLE |
| Scaling open (31Q targeted) | `model-scaling-v1` | 31 | **31/31 (100%)** | SCALING_EVIDENCE_STRONG |
| Scaling MCQ @ 0.5B | `model-scaling-v1` | 20 | **hybrid 13/20 vs trad 3/20** | HYBRID_MCQ_BEATS_TRAD |
| MCQ ladder (Qwen lm_patch) | `mcq-ladder-v1` | 10 | **0.5B 70% → 3.0B 100%** | MCQ_LADDER_SCALES |
| Backbone universality | `backbone-universality-v1` | 31 | **Valhalla 27/31 (87%)** | BACKBONE_INDEPENDENT_OPEN |
| External holdout | `external-holdout-v1` | 15 | **15/15 (100%)** | EXTERNAL_HOLDOUT_STRONG |

## 解读

- **RAGTruth (ACL 2024):** Context-grounded RAG faithfulness; native citation path; no abstain on QA slice.
- **Needle-in-haystack (session):** Session append recall @ depth 30 (62 lines); Paul Graham-style needle.
- **LongBench-v2 (THUDM):** Short MCQ slice; 12k context cap / 32 corpus lines; 0.5B hybrid lm_patch. Human full v2 ~53.7%.
- **Scaling open (31Q targeted):** Valhalla open backbone-invariant; +6.5pp premium @ 0.5B vs trad RAG.
- **Scaling MCQ @ 0.5B:** Hybrid lm_patch +50pp over trad prompt MCQ at same backbone.
- **MCQ ladder (Qwen lm_patch):** Rust sharded safetensors; 0.5B→3B hybrid MCQ scaling curve.
- **Backbone universality:** Tier B native open vs trad_lm RAG across Qwen/Gemma/Phi.
- **External holdout:** Out-of-suite generalization (complementary, not third-party corpus).

## Scaling 规律

- `TRAD_RAG_SCALES_WITH_PARAMS`
- `STRUCTURE_PREMIUM_NONNEGATIVE`
- `STRUCTURE_PREMIUM_LARGEST_AT_SMALL_BACKBONE`
- `HYBRID_MCQ_BEATS_TRAD_AT_SAME_BACKBONE`
- `TRAD_MCQ_SCALES_WITH_PARAMS`
- `TIER_B_OPEN_CEILING_STABLE`
- `MCQ_LADDER_SCALES`

## 复现

```bash
cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/run_recognized_benchmarks.py
```

JSON: `recognized_benchmarks_summary.json` · 分项报告见 `reports/valhalla_inference/`

---

*Rogue Intelligence LNC. · ValhallaBase · Qwen2.5-0.5B hybrid (unless noted)*
