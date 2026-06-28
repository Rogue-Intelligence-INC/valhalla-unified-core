# ValhallaBase 推理范式实验记录

> **Status:** Living document · **Updated:** 2026-06-26  
> **Scope:** 脱离传统 weight fine-tune 的 ValhallaBase 潜力验证  
> **Reports:** `../reports/` · monorepo mirror: `reports/valhalla_inference/`

---

## 1. 实验目标

在**不更新 LM 权重**（无 SGD / LoRA / fine-tune）前提下，客观测量 ValhallaBase 是否构成一种可复现的 **推理时 AI 范式**：

- 结构孵化（Triad + Fate）+ session snapshot + 定向 context ingest
- 与传统 Transformer「prompt = 全部上下文 + 梯度训练」对照

**诚实边界（所有实验预注册）：**

| 声称 | 不声称 |
|------|--------|
| 推理时 corpus-grounded AI | 替代全领域 weight fine-tune |
| Session 路由避免检索污染 | 无 context 的纯参数记忆 |
| 零权重 ingest + curriculum | 污染 session 全量 batch eval |

---

## 2. 协议索引

| 协议 ID | 脚本 | 报告 JSON |
|---------|------|-----------|
| `valhalla-base-training-potential-v2` | `tools/valhalla_inference/test_valhalla_base_training_potential.py` | `valhalla_base_training_potential_test_v2.json` |
| `valhalla-new-paradigm-potential-v1` | `tools/valhalla_inference/test_new_paradigm_potential.py` | `new_paradigm_potential_test.json` |
| `context-topic-drift-v1/v2` | `tools/valhalla_inference/test_context_topic_drift.py` | `context_topic_drift_*.json` |
| `local-corpus-demo-v1` | `tools/valhalla_inference/run_local_corpus_demo.py` | `local_corpus_demo_test.json` |
| `fate-output-gate-v1/v2` | `tools/valhalla_inference/test_fate_output_gate.py` | `fate_output_gate_test.json` |
| `proactive-fate-v1/v2` | `tools/valhalla_inference/test_proactive_fate_v2.py` | `proactive_fate_v2_test.json` |
| `confidence-report-v1` | `tools/valhalla_inference/run_confidence_report.py` | `confidence_report_v1.json` |
| `token-efficiency-v1` | `tools/valhalla_inference/test_token_efficiency.py` | `token_efficiency_test.json` |
| `mcq-coverage-v1` | `tools/valhalla_inference/test_mcq_coverage_v1.py` | `mcq_coverage_test.json` |

生产栈（所有实验默认）：

```python
ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",
    fate_qa_feedback=True,
)
```

---

## 3. 核心结果摘要（2026-06-26）

### 3.1 训练潜力 v2 (`TPI-v2 = 0.790`)

| 电池 | 结果 | 解读 |
|------|------|------|
| B1 语料规模 | 10%→100%：100%→96.8% | 定向 ingest 极度数据高效 |
| B2 学习范式 | isolated 96.8% / polluted 35.5% | 全量 dump + 同 session eval 不可用 |
| B4 Transfer | polluted 35.5% → transfer **96.8%** | Session 有价值，但须 fresh retrieval |
| B5 RAG gap | hybrid 96.8% / lm_patch 100% | open_retrieval 上 lm_patch 略优 |

**Verdict:** `STRONG_INFERENCE_TIME_LEARNING` · transfer 救援 polluted session (+61pp)

### 3.2 新范式潜力 v1 (`NPPI = 0.884`)

| 电池 | 结果 | 解读 |
|------|------|------|
| N1 合成新知识 | transfer = cold RAG = **83.3%** | 合成事实靠 ingest，不靠 snapshot 额外记忆 |
| N2 Fair holdout | cold = transfer = **96.8%** / polluted 35.5% | Holdout 上 session ≈ 定向 RAG |
| N3 组合改写 | 83.3%，lift 0pp | Curriculum 不增加 holdout 泛化 |
| N4 负对照 | integrity **100%** | targeted 91.7% vs distractor 0%；swap 4/4 |
| N5 范式分离 | hybrid 93.3% / lm_patch 100% | trad_lm 待本地权重 |

**证伪标记（诚实）：**

- `SESSION_SNAPSHOT_NO_HOLDOUT_LIFT_BEYOND_RAG`
- `FAIR_HOLDOUT_RAG_EQUIVALENT`
- `NOT_WEIGHT_FINE_TUNE_REPLACEMENT`

**Verdict:** `NEW_PARADIGM_VIABLE` · `SESSION_ROUTING_ESSENTIAL` · `METHODOLOGY_VALID`

### 3.3 Context drift（生产栈）

| 指标 | production arm |
|------|----------------|
| Swap fidelity | 12/12 |
| 30-turn on-topic | 29/30 |
| Cross-topic hallucination | 0 |

---

## 4. 方法论合法性清单

- [x] Holdout 与 fair ingest 语料 contamination audit（novel block clean）
- [x] 负对照：distractor / swap / wrong context
- [x] 零权重更新声明（结构路径，无 bake 变更）
- [x] 预注册证伪条件与 falsification flags
- [x] 分 slice 报告（open_retrieval / novel / compositional）
- [ ] traditional_lm 对照（需本机 Qwen 权重 + torch）

---

## 5. 推荐生产 eval 流程

```
1. ingest(定向 top-k per question)     # 非全量 dump
2. 可选 curriculum(QA + fate_qa_feedback)
3. eval / serve: 清空 corpus → per-question targeted append
4. 禁止: 在 80+ 行污染 session 上 batch eval
```

---

## 6. 复现命令

```bash
cd /path/to/Valhalla

# 训练潜力 v2
python3 tools/valhalla_inference/test_valhalla_base_training_potential.py --protocol v2

# 新范式潜力
python3 tools/valhalla_inference/test_new_paradigm_potential.py

# 本机语料 demo
python3 tools/valhalla_inference/run_local_corpus_demo.py \
  --corpus-dir valhalla-unified-core/docs

# Context drift
python3 tools/valhalla_inference/test_context_topic_drift.py
```

---

## 7. 本地语料 Demo（2026-06-26）

来源：`valhalla-unified-core/docs/`（优先 `VALHALLA_BASE_PLATFORM.md`、`FATE_INGRESS_ROUTING.md` 等）

| 阶段 | 准确率 |
|------|--------|
| 无本地语料（错误 context） | **0/8 (0%)** |
| cold targeted ingest | **8/8 (100%)** |
| teach 12 轮 + transfer | **8/8 (100%)**，train 66.7% |

**Lift:** ingest **+100pp** vs 无本地语料；teach 对 holdout **+0pp**（与 NPPI 一致：靠定向 ingest，不靠 snapshot 额外记忆）。

语料：60 行，主要来自 `VALHALLA_BASE_PLATFORM.md` 等优先文件。

复现：`python3 tools/valhalla_inference/run_local_corpus_demo.py`

---

## 9. Fate Output Gate v2 代数（2026-06-27）

见 [FATE_OUTPUT_GATE.md](./FATE_OUTPUT_GATE.md) §v2。公式 τ=12/(138+k)，Δ≥s₁/28；native margin 由 Rust 导出。

| 模式 | G1 coverage | emitted precision |
|------|-------------|-------------------|
| v2_algebraic | **93.5%** | **96.6%** |

Verdict: `FOG_V2_ALGEBRAIC_OK`

Verdict: `FOG_V2_ALGEBRAIC_OK`

---

## 10. Proactive Fate v2（2026-06-27）

**协议:** `proactive-fate-v2` · 40 trials（3 gates + 7 handcraft + 30 fair holdout pairs）

| 指标 | 值 | 含义 |
|------|-----|------|
| **PPI-v2** | **0.930** | 综合主动能力指数 |
| UP_on_topic | **100%** | 对齐语料+对话后，emit 的 nudge 全部 grounded |
| MAR | **88.9%** | mismatch 语料上 abstain / 无话题重叠 |
| FIR | **0%** | mismatch 上零幻觉 emit |
| Pass rate | **38/40 (95%)** | fair 仅 ZH_02/ZH_03 token 对齐缺口 |

**机制:** `proactive_idle` → 话题连续自探针（max overlap with prior）→ FOG 代数门控 → nudge

```bash
python3 tools/valhalla_inference/test_proactive_fate_v2.py
```

报告: `reports/valhalla_inference/PROACTIVE_FATE_V2_REPORT.md`

Verdict: `PROACTIVE_FATE_V2_STRONG` · `HIGH_UNSOLICITED_PRECISION` · `LOW_MISMATCH_INTERRUPT`

---

## 11. Confidence Report v1（2026-06-27，v1.1 补 trad_lm + 全量 proactive）

**协议:** `confidence-report-v1` — 汇总全部 inference 实验，统一 **Wilson 95%** + **Bootstrap 95%** 区间。

```bash
python3 tools/valhalla_inference/run_confidence_report.py
# 补 trad_lm 对照（需 .venv-llm）:
.venv-llm/bin/python3 tools/valhalla_inference/test_valhalla_base_training_potential.py --only-rag
.venv-llm/bin/python3 tools/valhalla_inference/test_new_paradigm_potential.py --only-n5
# 全量 proactive fair holdout:
python3 tools/valhalla_inference/test_proactive_fate_v2.py --fair-limit 0
```

报告: `reports/valhalla_inference/CONFIDENCE_REPORT_v1.md`

### Headline（带区间，诚实对外）

| 指标 | 点估计 | 95% CI |
|------|--------|--------|
| Fair holdout cold RAG | 96.8% | **[83.8%, 99.4%]** |
| Transfer vs polluted | +61.3pp | **[+45.2, +77.4]** |
| **Traditional LM RAG (Qwen2.5-0.5B)** | **96.8%** | **[83.8%, 99.4%]** |
| Valhalla vs trad_lm lift | +0.0pp | **[-9.7, +9.7]**（统计打平） |
| FOG emit precision | 96.6% | **[82.8%, 99.4%]** |
| Proactive UP \| emit | 100% | **[87.5%, 100%]**（n=27 emits，72 trials） |
| Proactive MAR (mismatch) | 88.2% | **[73.4%, 95.3%]** |
| 30-turn on-topic | 96.7% | **[83.3%, 99.4%]** |
| TPI-v2 | 0.790 | **[0.740, 0.823]** |
| NPPI | 0.884 | **[0.848, 0.984]** |
| PPI-v2 | 0.885 | **[0.823, 0.942]** |

**解读:** trad_lm 与 Valhalla hybrid **同分 30/31**；结构优势在 **session routing**（+61pp vs polluted）与 **FOG/proactive 门控**，非 raw RAG ceiling。lm_patch 100% 因 patch 头更贴 MCQ 格式。

**Global gaps:** ~~local demo~~ **local 20/20**；~~external ZH_GEO~~ **external 15/15**；MCQ deploy routing（`max_pick`）待全量 battery 刷新。

---

## 13. MCQ Coverage v1 + max_pick 路由（2026-06-28）

**协议:** `mcq-coverage-v1` — fair-1.2 test MCQ slice（n=46），生产栈 + Wilson CI。

```bash
python3 tools/valhalla_inference/test_mcq_coverage_v1.py --fast
.venv-llm/bin/python3 tools/valhalla_inference/test_mcq_coverage_v1.py --only-trad-lm
python3 tools/valhalla_inference/run_confidence_report.py
```

### 13.1 结果（lm_patch 生产默认，2026-06-28）

| 臂 | 结果 | Wilson 95% CI |
|----|------|---------------|
| **production hybrid lm_patch** | **30/46 (65.2%)** | [50.8%, 77.3%] |
| hybrid structure_fate | 14/46 (30.4%) | [19.1%, 44.8%] |
| native mcq_option | 14/46 (30.4%) | [19.1%, 44.8%] |
| oracle max(native, patch) | 32/46 (69.6%) | — |
| traditional LM + RAG | 13/46 (28.3%) | — |

**Verdict:** `MCQ_COVERAGE_STRONG` · Valhalla vs trad_lm **+37.0pp** [+21.7, +52.2]

**Disagreement（native vs patch）：** patch-only 18 · native-only 2 · both 12 · both wrong 14

### 13.2 P0：`mcq_decode=max_pick`（Rust deploy）

`ValhallaMcqDecode::MaxPick` — 每题并行跑 native `mcq_option` + lm_patch logprob，deploy 规则：

- 字母一致 → lm_patch
- patch 无字母 → native
- 不一致 → 默认 patch；native 胜当 `mcq_aggregate≥0.48` 且 `patch_conf≤0.45` 且 `margin≥0.08`

```python
ValhallaBase(decode="hybrid", mcq_decode="max_pick", ...)
```

报告: `reports/valhalla_inference/mcq_coverage_test.json` · `MCQ-coverage` in confidence report

---

## 14. Token Efficiency v1（2026-06-28）

**协议:** `token-efficiency-v1` — 30 轮对话 wire + prefill token 对照。

| 架构 | Wire 累计 | Prefill tokens | Holdout |
|------|-----------|----------------|---------|
| Valhalla append | 2,319 | 1,126 | 96.8% |
| RAG full resend | 14,268 | 3,868 | 96.8% |
| RAG + history | — | 11,845 | 96.8% |

**比率:** wire **0.16×** · prefill **0.29×**（question-only vs 全 corpus 重发）

```bash
python3 tools/valhalla_inference/test_token_efficiency.py
```

---

---

## 12. Crosslang Core Unified（2026-06-27）

**协议:** `crosslang-core-unified-v1` — 同一 production 栈，**language_switch=false**。

| 指标 | 值 |
|------|-----|
| CCU | **0.950** |
| core_unified | **6/6**（EN/ZH/FR 均 `[corpus:0]` 同文本） |
| External holdout | **15/15 (100%)** |

**Proactive Unicode:** CJK bigram + 中文 probe + overlap 门控 → ZH_02/03/04 全 pass，MAR **88.2%**。

```bash
python3 tools/valhalla_inference/test_crosslang_core_unified.py
python3 tools/valhalla_inference/test_external_holdout.py
```

---

## 15. 下一步

1. ~~补 traditional_lm RAG 对照~~ ✅（open + MCQ trad_lm）
2. MCQ `max_pick` 全量 battery 刷新 vs oracle 69.6%
3. stem-relative MCQ comparator（突破 70% 天花板）
4. 将 NPPI / TPI / MCQ / token-efficiency 同步 EN DD claims matrix

---

## 8. Fate Output Gate v1（2026-06-27，已被 v2 取代）

| 电池 | always emit | FOG emitted precision | FOG coverage / abstain |
|------|-------------|----------------------|-------------------------|
| G1 targeted | 96.8% | 93.3% | coverage 48.4% · abstain 16 |
| G2 distractor | 0.0% | — | abstain 11/12 |

**Verdict:** `FOG_V1_NEEDS_TUNING`
