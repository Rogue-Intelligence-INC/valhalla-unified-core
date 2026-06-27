# Valhalla Inference — Confidence Report v1

**Protocol:** `confidence-report-v1` · **Generated:** 2026-06-27

## Executive summary

| Domain | Key metric | 95% CI |
|--------|------------|--------|
| Grounding | fair_holdout_cold_rag | 96.8% [83.8%, 99.4%] |
| Session routing | transfer_vs_polluted_lift | +61.3pp [+45.2, +77.4] |
| vs Transformer | traditional_lm_rag | 96.8% [83.8%, 99.4%] |
| FOG quality | fog_emitted_precision | 96.6% [82.8%, 99.4%] |
| Proactive | UP_on_topic_given_emit | 100.0% [87.1%, 100.0%] |
| Crosslang | crosslang_accuracy | 100.0% [82.4%, 100.0%] |
| External | external_holdout_accuracy | 80.0% [54.8%, 93.0%] |
| Dialogue | extended_30turn_on_topic | 96.7% [83.3%, 99.4%] |

## Methods

| Statistic | Interval |
|-----------|----------|
| Proportions (accuracy, precision, abstain) | Wilson 95% |
| Paired lifts (pp) | Bootstrap paired 95% |
| TPI / NPPI / PPI | Bootstrap index 95% |

Display format: **point% [lo%, hi%]** or **index [lo, hi]**

## TPI-v2

Source: `valhalla_base_training_potential_test_v2.json` · Protocol: `valhalla-base-training-potential-v2`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| isolated_baseline_accuracy | 96.8% [83.8%, 99.4%] | 30/31 |
| polluted_session_accuracy | 35.5% [21.1%, 53.1%] | 11/31 |
| transfer_fresh_accuracy | 96.8% [83.8%, 99.4%] | 30/31 |
| transfer_vs_polluted_lift | +61.3pp [+45.2, +77.4] | paired n=31 |
| hybrid_vs_lm_patch_lift | -3.2pp [-9.7, +0.0] | paired n=31 |
| traditional_lm_rag | 96.8% [83.8%, 99.4%] | 30/31 |
| valhalla_over_traditional_lm | +0.0pp [-9.7, +9.7] | paired n=31 |
| TPI_v2 | 0.790 [0.740, 0.823] | bootstrap |

## NPPI

Source: `new_paradigm_potential_test.json` · Protocol: `valhalla-new-paradigm-potential-v1`

**Falsification flags:** `SESSION_SNAPSHOT_NO_HOLDOUT_LIFT_BEYOND_RAG`, `FAIR_HOLDOUT_RAG_EQUIVALENT`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| fair_holdout_cold_rag | 96.8% [83.8%, 99.4%] | 30/31 |
| fair_holdout_transfer | 96.8% [83.8%, 99.4%] | 30/31 |
| fair_transfer_vs_polluted | +61.3pp [+45.2, +77.4] | paired n=31 |
| negative_control_targeted | 91.7% [64.6%, 98.5%] | 11/12 |
| negative_control_distractor | 0.0% [0.0%, 24.2%] | 0/12 |
| swap_fidelity | 100.0% [51.0%, 100.0%] | 4/4 |
| n5_traditional_lm_rag | 96.8% [83.8%, 99.4%] | 30/31 |
| n5_hybrid_over_traditional_lm | +0.0pp [-9.7, +9.7] | paired n=31 |
| NPPI | 0.884 [0.848, 0.984] | bootstrap |

## FOG-v2

Source: `fate_output_gate_v2_test.json` · Protocol: `fate-output-gate-v2`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| always_emit_accuracy | 96.8% [83.8%, 99.4%] | 30/31 |
| fog_emitted_precision | 96.6% [82.8%, 99.4%] | 28/29 |
| fog_coverage | 93.5% [79.3%, 98.2%] | 29/31 |
| distractor_abstain_rate | 58.3% [32.0%, 80.7%] | 7/12 |

## Proactive-v2

Source: `proactive_fate_v2_test.json` · Protocol: `proactive-fate-v2`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| UP_on_topic_given_emit | 100.0% [87.1%, 100.0%] | 26/26 |
| on_topic_emit_rate | 74.3% [57.9%, 85.8%] | 26/35 |
| MAR_mismatch_abstain | 88.2% [73.4%, 95.3%] | 30/34 |
| FIR_on_mismatch_emits | 0.0% [0.0%, 49.0%] | 0/4 |
| PPI_v2 | 0.875 [0.811, 0.932] | bootstrap |

## Context-drift

Source: `context_topic_drift_test.json` · Protocol: `context-topic-drift-v1`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| swap_fidelity | 100.0% [75.8%, 100.0%] | 12/12 |
| swap_hallucination_rate | 0.0% [0.0%, 24.2%] | 0/12 |
| distractor_false_confidence_rate | 0.0% [0.0%, 24.2%] | 0/12 |

## Context-drift-extended

Source: `context_topic_drift_extended_test.json` · Protocol: `context-topic-drift-v2`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| extended_30turn_on_topic | 96.7% [83.3%, 99.4%] | 29/30 |

## Local-corpus

Source: `local_corpus_demo_test.json` · Protocol: `local-corpus-demo-v1`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| before_no_corpus | 0.0% [0.0%, 16.1%] | 0/20 |
| cold_targeted | 70.0% [48.1%, 85.5%] | 14/20 |
| after_transfer | 70.0% [48.1%, 85.5%] | 14/20 |
| ingest_vs_none_lift | +70.0pp [+50.0, +90.0] | paired n=20 |

## Crosslang-core

Source: `crosslang_core_unified_test.json` · Protocol: `crosslang-core-unified-v1`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| crosslang_accuracy | 100.0% [82.4%, 100.0%] | 18/18 |
| core_unified_fact_rate | 100.0% [61.0%, 100.0%] | 6/6 |
| line_agreement_rate | 100.0% [61.0%, 100.0%] | 6/6 |
| CCU | 0.950 [0.950, 0.950] | bootstrap |

## External-holdout

Source: `external_holdout_test.json` · Protocol: `external-holdout-v1`

| Metric | Estimate [95% CI] | n |
|--------|-------------------|---|
| external_holdout_accuracy | 80.0% [54.8%, 93.0%] | 12/15 |

## Global gaps

- local demo n=8 → ingest lift CI degenerates at +100pp
- Composite indices bootstrap uses row resampling — point may differ slightly from stored index

## Reproduce

```bash
python3 tools/valhalla_inference/run_confidence_report.py
```
