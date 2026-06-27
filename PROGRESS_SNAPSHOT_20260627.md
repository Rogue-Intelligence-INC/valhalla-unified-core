# Valhalla Unified Core — Progress Snapshot

> **Timestamp:** 2026-06-27 08:11 CST · 2026-06-27 00:11 UTC  
> **Git target:** `valhalla-unified-core` · commit after inference-paradigm experiment pack

---

## 里程碑摘要

| 领域 | 状态 | 关键指标 |
|------|------|----------|
| Context binding / drift | ✅ 生产栈验证 | swap 12/12 · 30-turn 29/30 · 0 hallucination |
| 训练潜力 v2 (TPI) | ✅ 完成 | **TPI-v2 = 0.790** · transfer 救援 polluted +61pp |
| 新范式潜力 (NPPI) | ✅ 完成 | **NPPI = 0.884** · 负对照 integrity 100% |
| 本机语料 demo | ✅ 完成 | none 0% → ingest **100%** (8/8) |
| 工程文档 | ✅ 更新 | `EXPERIMENT_RECORD_INFERENCE_PARADIGM.md` |
| traditional_lm 对照 | ⏸ 待补 | 本机需 torch + Qwen 权重 |

---

## 核心结论（诚实）

1. **ValhallaBase = 推理时结构化 RAG + Session 路由**（零权重更新）
2. **Holdout 上 session snapshot 不超出 cold RAG**（证伪：非 fine-tune 替代品）
3. **Polluted session batch eval 不可用**；正确路径：train → 清空 corpus → per-question targeted append
4. **本机 markdown ingest 有效**：平台文档 60 行 → 8 题全对

---

## 新增协议 & 报告

| 协议 | 报告 |
|------|------|
| `valhalla-base-training-potential-v2` | `reports/valhalla_base_training_potential_test_v2.json` |
| `valhalla-new-paradigm-potential-v1` | `reports/new_paradigm_potential_test.json` |
| `local-corpus-demo-v1` | `reports/local_corpus_demo_test.json` |
| `context-topic-drift-v1/v2` | `reports/context_topic_drift_*.json` |

Monorepo 脚本（licensed checkout）：`tools/valhalla_inference/test_*.py` · `run_local_corpus_demo.py`

---

## 生产推荐栈

```python
ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_ingress_routing="quad_cycle",
    fate_qa_feedback=True,
)
```

---

## 下一步

1. 补 traditional_lm RAG baseline（`.venv-llm` + Qwen2.5-0.5B）
2. EN DD claims matrix 同步 NPPI / TPI 数值
3. 可选：46 MCQ 三臂 multimodal-no-fusion ablation

---

*Generated for push checkpoint 2026-06-27.*
