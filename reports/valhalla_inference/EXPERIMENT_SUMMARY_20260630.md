# ValhallaBase — 公认 & Industry Benchmark 实验总结

**Date:** 2026-06-30 · **Stack:** ValhallaBase hybrid · Qwen2.5-0.5B-Instruct (default)  
**Runner:** `run_industry_benchmarks.py` · `run_recognized_benchmarks.py`  
**有效解读（必读）：** [`VALID_BENCHMARKS_INTERPRETATION_20260630.md`](VALID_BENCHMARKS_INTERPRETATION_20260630.md)  
**JSON:** `valid_benchmarks_summary.json` · `industry_benchmarks_summary.json`

---

## 1. 总表（2026-06-30 industry 全量 · 加强下载后）

| # | Benchmark | 有效性 | 次数 | Result | Verdict |
|---|-----------|--------|------|--------|---------|
| 1 | **RAGTruth** | A | ×2 | **40/40 (100%)** | RAGTRUTH_STRONG |
| 2 | **RAGTruth-100** | A | ×1 | **100/100 (100%)** | RAGTRUTH_STRONG |
| 3 | **Needle session** | A | ×2 | **4/4 (100%)** | NEEDLE_STRONG |
| 4 | **RULER-style** | A | ×1 | **20/20 (100%)** | NEEDLE_STRONG |
| 5 | **External holdout** | A | ×1 | **15/15 (100%)** | EXTERNAL_HOLDOUT_STRONG |
| 6 | **MCQ ladder** | A | ×1 (46Q) | **0.5B 65% → 3B 98%** | MCQ_LADDER_SCALES |
| 7 | **MultiHop-RAG** | B | ×1 | **9/25 (36%)** | OPEN_QA_DEVELOPING |
| 8 | **LongBench-v2** | B | ×1 | **7/20 (35%)** | LONGBENCH_V2_VIABLE |
| 9 | **LaRA RAG vs LC** | B | ×1 | RAG **25%** vs LC **70%** | STRUCTURE_RAG_BELOW_LC |
| 10 | **LoCoMo** | B† | ×1 | **1/30 (3%)** | OPEN_QA_DEVELOPING |
| 11 | **FRAMES** | C | — | 0/25 | **FRAMES_NEEDS_WIKI** |
| 12 | **Scaling open** | A | ×1 | Valhalla **31/31 (100%)** | SCALING_EVIDENCE_STRONG |

有效性：**A**=可对外 cite · **B**=须说明条件 · **C**=无效勿 cite。详见 [有效解读](VALID_BENCHMARKS_INTERPRETATION_20260630.md)。

---

## 2. 对外一句话（仅 Tier A）

> **RAGTruth 100/100 · Needle 4/4 · RULER 20/20 · Holdout 15/15 · MCQ 65%→98%** — RAG 忠实与会话召回 industry 级；Tier B 为诚实边界；FRAMES/LoCoMo 分数勿直接对外。

---

## 3. 分项要点

### RAGTruth ✅
- 40Q **×2** + 100Q **×1**；metric = **context-grounded**；0 abstain  

### Needle + RULER ✅
- Needle **×2** · depth 30 · RULER 20/20 **×1**

### MCQ ladder ✅
- **46 题 full fair MCQ**（非 10 题 fast slice）：0.5B **30/46** → 3B **45/46**

### MultiHop / LaRA / LoCoMo ⚠️
- 见 [有效解读 §2](VALID_BENCHMARKS_INTERPRETATION_20260630.md#2-tier-b--有效数据分数须带条件说明)

### FRAMES ❌
- **无效** — 无 Wikipedia corpus；勿 cite 0%

---

## 4. 复现

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
HF_ENDPOINT=https://hf-mirror.com .venv-llm/bin/python3 tools/standard_benchmarks/download_standard_benchmarks.py --all --no-wiki-fetch
RUSTFLAGS="-L /opt/cuda/lib64" python3 tools/valhalla_inference/run_industry_benchmarks.py --all
```

| 报告 | 文件 |
|------|------|
| **有效解读（主文档）** | `VALID_BENCHMARKS_INTERPRETATION_20260630.md` |
| Industry 汇总 | `INDUSTRY_BENCHMARKS_20260630.md` |
| 本总结 | `EXPERIMENT_SUMMARY_20260630.md` |
| JSON | `valid_benchmarks_summary.json` |

---

*Rogue Intelligence LNC. · 2026-06-30*
