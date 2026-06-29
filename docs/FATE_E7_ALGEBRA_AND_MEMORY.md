# Fate · E7 Algebra · Long Memory · Proactive v2

> **Version:** 1.0 · **Date:** 2026-06-30  
> **Code:** `manifestsys/hub-f64/src/e7_algebra.rs` · `signal_ingress.rs` · `native_qa.rs` · `valhalla_base.rs`

---

## E7 代数（无拟合 float）

整数：r=7, δ=5, dim=133, base_α=138

| 符号 | 公式 | 用途 |
|------|------|------|
| τ(k) | (r+δ)/(dim+δ+k) = **12/(138+k)** | FOG 阈值、affinity 正反馈、open rerank（可选） |
| Δ(s₁) | s₁·δ/(dim+r) = **s₁·5/140** | FOG margin 门 |
| affinity⁺ | align·τ(0) | QA 正确 → line affinity ↑ |
| affinity⁻ | align·δ/(dim+r) | QA 错误 → line affinity ↓ |
| QA pass/fail | τ(0) / δ/(dim+r) | Fate + Tile/Stem passive 强度 |

**Fate 接入：**

- `feedback_qa_outcome` — quad 路由强度用代数  
- `feedback_corpus_line_structural` — line 级 grinder 对齐 → 主 quad  
- `apply_corpus_retrieval_feedback` — snapshot `corpus_line_affinity[]`  
- `fate_telemetry.algebra_formula` = `e7_tau_v1`

---

## 长久记忆（long-memory-v1）

**生产栈：** hybrid + native_follow_up_aware + fate_qa_feedback + cycles=2

| 电池 | 结果 |
|------|------|
| early_anchor | 3/3 |
| extended_20 | 57/60 |
| session_reload | 10/10 |
| corpus_depth | 3/3 |
| **overall** | **73/76 (96.0%)** |

机制：结构 rerank + session IDF + follow-up boost + FOG（有 citation 则 emit）+ line affinity **学习写入 snapshot**（rerank 默认 weight=0，避免同线程串扰）。

脚本：`tools/valhalla_inference/test_long_memory_v1.py`  
报告：`reports/valhalla_inference/LONG_MEMORY_OPTIMIZATION_20260628.md`

---

## Proactive Fate v2（2026-06-30）

| 指标 | 值 |
|------|-----|
| Pass | **72/72 (100%)** |
| PPI-v2 | **0.921** |
| UP on-topic | 100% |
| MAR mismatch abstain | 97.1% |
| FIR | 0% |

Fair aligned：`targeted_context` + 3-turn warmup + conservative defer pass。  
探针：GDP 缩写、单数字 overlap。

脚本：`tools/valhalla_inference/test_proactive_fate_v2.py`

---

## 相关测试

```bash
python3 tools/valhalla_inference/test_fate_algebra_corpus_v1.py
python3 tools/valhalla_inference/test_long_memory_v1.py --arm production
python3 tools/valhalla_inference/test_proactive_fate_v2.py
python3 tools/valhalla_inference/test_external_holdout.py   # 15/15
```

---

*Proprietary — Rogue Intelligence LNC.*
