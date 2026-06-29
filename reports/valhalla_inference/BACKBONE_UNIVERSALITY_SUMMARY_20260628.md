# Backbone 普世性实验总结

**Date:** 2026-06-28  
**Protocol:** `backbone-universality-v1`  
**Script:** `tools/valhalla_inference/test_backbone_universality_v1.py`

---

## 1. 目标

验证 Valhalla **结构层（Tier B hybrid open）** 是否与 LM decode backbone 无关；对照 **trad_lm RAG** 在 Qwen / Gemma / Phi-3 上的表现。

**不在本协议：** Rust `lm_patch`（Candle **仅 Qwen2**）。

---

## 2. 模型与下载路径

| 模型 | 大小 | 下载路径 |
|------|------|----------|
| `Qwen/Qwen2.5-0.5B-Instruct` | 已有 | HF cache |
| `microsoft/Phi-3-mini-4k-instruct` | ~7.6GB | **hf-mirror.com**（xethub 超时后 resume） |
| `google/gemma-2-2b-it` | ~5.2GB | **ModelScope**（mirror gated fallback） |

`huggingface.co` 直连不通；使用：

```bash
.venv-llm/bin/python3 tools/valhalla_inference/download_backbone_models.py --mirror
.venv-llm/bin/python3 tools/valhalla_inference/download_backbone_models.py --endpoint modelscope --only gemma
```

---

## 3. 结果摘要

### 3.1 open_retrieval holdout（n=31，与 confidence report 对齐）

| 臂 | 结果 | 备注 |
|----|------|------|
| **Valhalla hybrid** | **28/31 (90.3%)** | 结构栈固定，与 backbone 无关 |
| trad_lm Qwen-0.5B | 31/31 (100%) | |
| trad_lm Gemma-2-2b | 31/31 (100%) | |
| trad_lm Phi-3-mini | 31/31 (100%) | |

JSON: `backbone_universality_open_retrieval_full.json`

**vs 生产 holdout 96.8% (30/31)：** 本协议 per-question `corpus_for_prompt`，非 transfer battery 全协议 → **−6.5pp** 可解释差异。

### 3.2 external holdout（n=15）

| 臂 | 结果 |
|----|------|
| **Valhalla hybrid** | **15/15 (100%)** |
| trad_lm Qwen-0.5B | 14/15 (93.3%) |
| trad_lm Gemma-2-2b | 15/15 (100%) |
| trad_lm Phi-3-mini | 15/15 (100%) |

JSON: `backbone_universality_external_full.json`

### 3.3 fair 全 open（n=61，含 open_generation）

| 臂 | 结果 |
|----|------|
| Valhalla hybrid | 28/61 (45.9%) |
| trad_lm Qwen-0.5B | 56/61 (91.8%) |
| trad_lm Gemma-2-2b | 60/61 (98.4%) |
| trad_lm Phi-3-mini | 59/61 (96.7%) |

JSON: `backbone_universality_fair_open_full.json`

**解读：** open_generation 无 corpus → Valhalla native 系统性偏低；**不可与 holdout 31 题混读**。

### 3.4 smoke（n=8）

Valhalla 7/8 (87.5%) · 三 trad_lm 均 8/8。

---

## 4. 结论

| 声称 | 证据 |
|------|------|
| Valhalla 结构层 **backbone 无关** | 同一 hybrid 栈；external **100%** |
| trad_lm **跨架构可跑通** | Gemma (ModelScope) + Phi-3 (mirror) + Qwen 均加载成功 |
| 更大 trad_lm 在 open_generation 上更高 | Gemma/Phi **98–100%** vs Qwen **92%**（61 题） |
| open_retrieval 上 trad_lm 31/31 | 本协议 RAG 略优于 Valhalla **90.3%** — 与 holdout 打平结论需同一 eval 协议再验 |
| lm_patch 普世性 | **未声称** — Qwen2-only |

### 证伪标记

- `BACKBONE_UNIVERSALITY_STRUCTURE_INDEPENDENT` ✅（结构路径）
- `TRAD_LM_BACKBONE_SCALES_ON_OPEN_GENERATION` ✅（61 题）
- `OPEN_RETRIEVAL_TRAD_LM_DOMINATES_IN_THIS_PROTOCOL` ⚠️（31 题 100% vs 90.3%，协议差）

---

## 5. 复现

```bash
.venv-llm/bin/python3 tools/valhalla_inference/download_backbone_models.py --mirror

RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base

.venv-llm/bin/python3 tools/valhalla_inference/test_backbone_universality_v1.py --slice open_retrieval
.venv-llm/bin/python3 tools/valhalla_inference/test_backbone_universality_v1.py --suite external
```

---

## 6. 关联

- Stem/Tile 分析：`STEM_TILE_ORGAN_AGGREGATION_ANALYSIS_20260628.md`
- 实验记录：VUC `EXPERIMENT_RECORD_INFERENCE_PARADIGM.md` §17
