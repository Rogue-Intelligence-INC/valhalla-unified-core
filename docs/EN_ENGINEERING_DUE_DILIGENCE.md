# Valhalla Unified Core — Engineering Due Diligence Pack

**Document type:** Technical due diligence (DD)  
**Product:** Valhalla Unified Core (VUC)  
**Version:** vuc-dd-1.0 · **Date:** 2026-06-26  
**Publisher:** Rogue Intelligence LNC.  
**Audience:** Investor engineers, acquirer tech teams, enterprise security review  
**Status:** Artifact-indexed; all headline metrics trace to JSON in `reports/`

---

## 1. DD scope

This pack supports review of:

1. **Claims validity** — Are marketing highlights backed by defined protocols?  
2. **Reproducibility** — Can an auditor re-run benchmarks?  
3. **Architecture separation** — ValhallaBase vs baked LM loader  
4. **Risk register** — Known gaps and mitigations  
5. **IP & license** — Proprietary boundary  

---

## 2. Claims ↔ evidence matrix

| Claim | Metric | Protocol | Primary artifact |
|-------|--------|----------|------------------|
| Grounded open QA | 97% (30/31) | scale-benchmark-v1 | `reports/scale_benchmark_test.json` |
| No distractor hallucination | 0% false confidence | context-topic-drift-v1 | `reports/context_topic_drift_test.json` |
| Context swap works | 100% fidelity (12/12) | context-topic-drift-v1 | `reports/context_topic_drift_test.json` |
| No cross-topic hallucination | 0/48 combined probes* | context-topic-drift-v1/v2 | drift JSON files |
| Long-session stability | 96.7% on-topic @ 30 turns | context-topic-drift-v2 | `reports/context_topic_drift_extended_test.json` |
| Multimodal fusion superiority | 107/107 non-iso wins | valhalla-universal-core-v1 | `reports/scale_benchmark_test.json` |
| Core fusion helps QA | 75% vs 66.7% (12 tasks) | context-core-fusion-v2 | `reports/context_core_fusion.json` |
| MCQ hybrid lm_patch | 65.2% (30/46) | mcq-coverage-v1 | `reports/valhalla_inference/mcq_coverage_test.json` |
| MCQ vs trad_lm RAG | +37.0pp | mcq-coverage-v1 | paired n=46 in confidence report |
| MCQ oracle ceiling | 69.6% (32/46) | mcq-coverage-v1 | max(native, patch) — not deployable |
| Token wire efficiency | 0.16× vs RAG | token-efficiency-v1 | `reports/valhalla_inference/token_efficiency_test.json` |
| Token prefill efficiency | 0.29× vs RAG | token-efficiency-v1 | 30-turn matched holdout 96.8% |
| Confidence composite | TPI 0.790 / NPPI 0.884 | confidence-report-v1 | `reports/valhalla_inference/confidence_report_v1.json` |
| Local corpus demo | 100% (20/20) | local-corpus-demo-v1 | `reports/valhalla_inference/local_corpus_demo_test.json` |
| External holdout | 100% (15/15) | external-holdout-v1 | `reports/valhalla_inference/external_holdout_test.json` |
| Fate ingress default | quad_cycle 93.3% P1 | fate ingress ladder | `reports/fate_weight_ladder_compare_30.json` |
| QA→Fate learning | Topic prefs differentiate | fate-qa-feedback | `reports/fate_qa_feedback_40.json` |
| Stem organ clusters form | BFS connected components @ runtime | stem-tile-structure-analysis-v1 | `signal_ingress.rs` + persistent MCQ logs |
| Tile aggregation (merge) | ~11 completed tiles @ 49-line corpus | stem-tile-structure-analysis-v1 | `tile_complete.rs` + `TILE_STEM_WHOLE_QUESTION` |
| Native MCQ persistent lift (tile) | 47.8% vs 28.3% isolated (+19.6pp) | TILE_STEM whole_question | `reports/experiments/TILE_STEM_WHOLE_QUESTION_20260622_0249.json` |
| Structure-only MCQ (not production) | 30.4% — below lm_patch 65.2% | mcq-coverage-v1 | `mcq_coverage_test.json` |
| Structure hybrid backbone-independent | external 15/15; open_retrieval 28/31 (single Valhalla run) | backbone-universality-v1 | `backbone_universality_*_full.json` |
| trad_lm cross-arch load | Qwen + Gemma-2-2b + Phi-3-mini | backbone-universality-v1 | `download_backbone_models.py` |
| lm_patch backbone scope | Qwen2-only (Rust Candle) — not universal | engineering limit | documented §17 |

\*Combined: 12 swap + 6 interleave + 30 extended = 48 cross-topic checks; **0 forbidden-entity hallucinations** on production arm.

---

## 3. Architecture DD checklist

| Item | Status | Notes |
|------|--------|-------|
| ValhallaBase binary builds | ✅ | `cargo build -p hub-f64 --bin valhalla_base` |
| Protocol versioning | ✅ | IDs in JSON `protocol` fields |
| Session isolation per trial | ✅ | Drift v1; persistent only in battery E |
| Hybrid routing documented | ✅ | `VALHALLA_BASE_PLATFORM.md` |
| Two deployment paths documented | ✅ | Base vs ValhallaLLM — see whitepaper §2.2 |
| Bake manifest schema | ✅ | `PROTOCOL.md` |
| Fair benchmark decontamination | ✅ | fair-1.2 suite |

---

## 4. Benchmark methodology (auditor summary)

### 4.1 Fair benchmark

- **Suite:** `fair-1.2` · splits smoke/val/test  
- **Corpus:** decontaminated ingest lines; open_retrieval slice = questions answerable from corpus  
- **Scoring:** `score_answer()` — keyword/reference match; MCQ strict `ANSWER: X`

### 4.2 Context-topic drift

- **Fixed specs** — hints/forbidden lists predefined (not model-derived)  
- **Arms** — production (`hybrid` + `native_follow_up_aware`) vs controls  
- **Hallucination definition** — forbidden cross-topic token in answer (word-boundary aware for numerics)  
- **Negative control** — `hybrid_follow_up_lm` shows 10% hallucination @ 30 turns (do not ship)

### 4.3 Universal core

- **Compare layout** — isolated vs non-isolated on identical task samples  
- **Primary metric** — `shared_patch_pairwise_avg`, `universal_core_score`

---

## 5. Artifact inventory

| File | Description |
|------|-------------|
| `scale_benchmark_test.json` | 107-task core + 46 MCQ + open slices |
| `context_topic_drift_test.json` | Batteries A–D |
| `context_topic_drift_extended_test.json` | Battery E (30-turn) |
| `context_core_fusion.json` | Baseline vs core_fusion (12 tasks) |
| `context_flexibility_max_goal.json` | Follow-up decode comparison |
| `fate_weight_ladder_compare_30.json` | Ingress mode ablation |
| `fate_qa_feedback_40.json` | QA→Fate closed loop |
| `cross_modal_test_summary.json` | 12-task tri-modal alignment |
| `base_load_fused_crossmodal12.json` | Baked LM load smoke |

Full monorepo mirror: `Valhalla/reports/valhalla_inference/`

---

## 6. Reproduction commands

Auditor machine requirements: Linux, CUDA optional, Rust toolchain, Python 3.11+, Valhalla license checkout.

```bash
cd Valhalla
RUSTFLAGS='-L /opt/cuda/lib64' cargo build -p hub-f64 --release --bin valhalla_base

# Drift + hallucination ( ~2 min native-only )
python3 tools/valhalla_inference/test_context_topic_drift.py --phase test --skip-trad
python3 tools/valhalla_inference/test_context_topic_drift.py --battery-e-only --skip-trad

# Scale context + MCQ
python3 tools/valhalla_inference/run_scale_benchmark.py --phase test --skip-core --skip-open

# Core fusion
python3 tools/valhalla_inference/test_context_core_fusion.py --limit 12
```

Expected production arm highlights after rerun: swap 12/12, extended 29/30 on-topic, 0 cross-topic hallucinations.

---

## 7. Risk register

| ID | Risk | Severity | Mitigation | Status |
|----|------|----------|------------|--------|
| R1 | MCQ 65% deploy vs enterprise bar | Medium | LM logprob compose; stem-relative MCQ | In roadmap |
| R2 | Core fusion hurts MCQ @ 46 on hash modalities | Medium | Auto-enable fusion only with real mm; text-only default | Documented |
| R3 | ValhallaLLM path not drift-tested | Medium | Add Base vs baked-loader parity suite | Planned |
| R4 | open_generation 0% | Low | By design; use LM path or corpus expansion | Accepted |
| R5 | mcq_fate / structure_fate 30.4% | Low | Not production MCQ path; ship lm_patch | Accepted |
| R8 | Stem organ = 1 mega-cluster @ fair corpus | Medium | min_cells tuning; larger corpus; stem-relative MCQ | Documented |
| R9 | Tile/stem parallel fusion no lift | Low | Do not ship 0.5+0.5 merge; use tile_fate track | Accepted |
| R6 | Proprietary license friction | Business | Evaluation NDA + pilot SLA | Process |
| R7 | Binary/build CUDA linkage | Ops | Document RUSTFLAGS; CPU fallback | Documented |

---

## 8. Security & data handling

| Topic | Posture |
|-------|---------|
| Customer corpus | Processed locally in incubation; no default cloud exfiltration in OSS tools |
| Model weights | Customer bake stays on-prem; HF export standard format |
| API surface | JSON stdin/stdout — embed behind customer gateway |
| Audit trail | `[corpus:k]` citations + JSON row logs per question |

---

## 9. IP boundary

| In scope (Rogue Intelligence LNC.) | Out of scope |
|-----------------------------------|--------------|
| Triad body, Fate, universal core layout | Customer corpus content |
| ValhallaBase protocols & benchmarks | Third-party Qwen weights (base model license) |
| Bake pipeline & manifest | S-wind / physics simulation stack (separate) |

See [NON_OPEN_SOURCE.md](../NON_OPEN_SOURCE.md).

---

## 10. Open questions for management

1. Primary GTM: ValhallaBase API vs baked vLLM SKU?  
2. MCQ target SLA for enterprise (70% vs 80%)?  
3. Timeline for ValhallaLLM drift parity tests?  
4. Multi-tenant Fate feedback — privacy model?  

---

## 11. Contact

Technical diligence: provide GitHub access to this repo + Valhalla monorepo under NDA.  
**licensing@rogue-intelligence.com**

Copyright © 2026 Rogue Intelligence LNC. All Rights Reserved.
