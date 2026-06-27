# Proactive Fate v2 — Experiment Report

**Protocol:** `proactive-fate-v2` · **Date:** 2026-06-27

## Headline

| Metric | Value |
|--------|-------|
| **PPI-v2** (composite) | **0.930** |
| On-topic unsolicited precision | 100.0% |
| On-topic emit rate | 89.5% |
| Mismatch abstain rate | 88.9% |
| False interrupt rate | 0.0% |
| Trigger rate (eligible) | 51.3% |

## Verdict

- `PROACTIVE_FATE_V2_STRONG`
- `HIGH_UNSOLICITED_PRECISION`
- `LOW_MISMATCH_INTERRUPT`
- `NO_HALLUCINATION_ON_MISMATCH`
- `GATES_OK`

## Batteries

- Gates: 3/3
- Handcraft: 7/7
- Fair holdout: 28/30

## Known gaps

- Fair `ZH_*` aligned cases may fail `no_topic_overlap` when warmup tokens do not match ASCII corpus tokenization (2/30 fair).
- On-topic emit rate <100% by design: FOG + topic gate defer low-confidence probes.

## Reproduce

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_proactive_fate_v2.py
```

JSON: `reports/valhalla_inference/proactive_fate_v2_test.json`

