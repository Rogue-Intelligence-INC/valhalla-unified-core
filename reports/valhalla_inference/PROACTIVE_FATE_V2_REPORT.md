# Proactive Fate v2 — Experiment Report

**Protocol:** `proactive-fate-v2` · **Date:** 2026-06-29

## Headline

| Metric | Value |
|--------|-------|
| **PPI-v2** (composite) | **0.921** |
| On-topic unsolicited precision | 100.0% |
| On-topic emit rate | 80.0% |
| Mismatch abstain rate | 97.1% |
| False interrupt rate | 0.0% |
| Trigger rate (eligible) | 42.0% |

## Verdict

- `PROACTIVE_FATE_V2_STRONG`
- `HIGH_UNSOLICITED_PRECISION`
- `LOW_MISMATCH_INTERRUPT`
- `NO_HALLUCINATION_ON_MISMATCH`
- `GATES_OK`

## Batteries

- Gates: 3/3
- Handcraft: 7/7
- Fair holdout: 62/62

## Known gaps

- Fair aligned uses `targeted_context` + 3-turn warmup; conservative defer (spread / no_topic_overlap) counts as pass.
- Exit: PPI-v2 ≥ 0.75 + gates OK + FIR ≤ 5% (binary 85% is secondary).

## Reproduce

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_proactive_fate_v2.py
```

JSON: `reports/valhalla_inference/proactive_fate_v2_test.json`

