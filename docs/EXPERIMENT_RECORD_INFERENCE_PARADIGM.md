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

## 8. 下一步

1. 补 traditional_lm RAG 对照（`.venv-llm` + 本地 Qwen）
2. v3：跨 session 持久化（若产品需要）与 feedback lift 专项
3. 将 NPPI / TPI 写入 EN_ENGINEERING_DUE_DILIGENCE claims matrix
