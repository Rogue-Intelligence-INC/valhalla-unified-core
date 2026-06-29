# 长久记忆 — Valhalla 哲学对齐路线

**Date:** 2026-06-28 (updated 2026-06-29)  
**Protocol:** `long-memory-v1`  
**Script:** `tools/valhalla_inference/test_long_memory_v1.py`

---

## 原则（不强行凑分）

Valhalla native open 检索的**自然排序**应为：

1. **结构优先** — `score_memories`：grinder 信号 cosine + incubated patch + Tile/Stem 对齐  
2. **会话统计 tie-break** — 当前 session corpus 的 IDF（无外部索引、无领域词表）  
3. **会话历史** — `question_history` + `follow_up_retrieval_boost`（已有机制）  
4. **代数门控** — FOG 在证据不足时 **abstain**，不用启发式惩罚硬推答案  
5. **结构学习** — `fate_qa_feedback` + **line-level corpus affinity**（信号 cosine，非关键词表）

**刻意不做：**

- WH 词 / continent / capital 等**句式规则表**（曾短期 76/76，已移除）  
- 实体-only 重叠的**负向惩罚**逼排序  
- 为 benchmark 叠加 `keyword_domain_boost` 于 open 路径（MCQ/legacy 仍保留）

---

## 已实现（123 三项）

| # | 机制 | 实现 |
|---|------|------|
| 1 | Fate QA → line-level structural affinity | `TriadSession.apply_corpus_retrieval_feedback`：Q↔line grinder cosine × pos/neg；snapshot 持久化 `corpus_line_affinity` |
| 2 | Open structure weight env | `VALHALLA_OPEN_STRUCTURE_WEIGHT`（默认 **1.2**）缩放 cosine + patch + Tile/Stem |
| 3 | FOG abstain on open | `VALHALLA_OPEN_FOG_ENFORCE`（默认 **on**）；**保留** `[corpus:N]` 结构检索 citation，仅拦截无 citation 的幻觉路径 |

Line affinity rerank：`affinity × Q↔line_align × weight`（当前问与行结构对齐才生效）。

默认 `VALHALLA_CORPUS_LINE_AFFINITY_WEIGHT=0`（学习写入 snapshot，rerank 需显式开启；0.18 在长 session 压测有回归，见下）。

---

## 保留的 native 修复（非预设结论）

| 机制 | 性质 |
|------|------|
| Negation-aware 关键词 | 文本结构（`not the X`），非领域清单 |
| 小数 span | 解析正确性（`9.8` 不断句） |
| `question_history` cap | 会话资源边界（默认 12） |
| `session_idf_term_boost` | session 内 DF→IDF，**仅正向** tie-break |

Env：`VALHALLA_SESSION_IDF_TERM_WEIGHT`（默认 0.08）· `VALHALLA_MEMORY_RECENCY_WEIGHT` · `VALHALLA_QUESTION_HISTORY_MAX`

---

## 复现

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_long_memory_v1.py
python3 tools/valhalla_inference/test_context_flexibility_goal.py
```

报告 JSON：`long_memory_test_full.json`

---

## 实测（结构优先栈 + 123，默认 affinity weight=0）

| 电池 | n | 结果 |
|------|---|------|
| early_anchor | 3 | **3/3 (100%)** |
| extended_20 | 60 | **57/60 (95.0%)** |
| session_reload | 10 | **10/10 (100%)** |
| corpus_depth | 3 | **3/3 (100%)** |
| **overall** | 76 | **73/76 (96.0%)** |

典型未命中（可接受边界）：australia 同线程 append-then-ask 近因混淆（capital vs language / Melbourne vs Canberra）；physics 动量行重复 — **结构 tie-break 边界**，不用 WH 规则表强推。

Affinity 实验：`VALHALLA_CORPUS_LINE_AFFINITY_WEIGHT=0.18` → **69/76**（line 全局 affinity 在同线程多问题上串扰）；对齐门控后仍 ~69，故默认关闭 rerank 权重。

JSON: `long_memory_test_full.json`

---

## Env 汇总（新增）

| 变量 | 默认 | 说明 |
|------|------|------|
| `VALHALLA_OPEN_STRUCTURE_WEIGHT` | 1.2 | open rerank 结构项缩放 |
| `VALHALLA_CORPUS_LINE_AFFINITY_WEIGHT` | **0** | line affinity rerank；设 `algebra` 或 `tau` 用 τ(k) |
| `VALHALLA_CORPUS_AFFINITY_POS` / `NEG` | τ(0)·align / δ/(dim+r)·align | QA feedback 更新（env 可覆盖 scale） |
| `VALHALLA_OPEN_FOG_ENFORCE` | true | open 无 citation 时 FOG abstain |

---

## 与生产 holdout 关系

Open holdout **96.8%** 使用 transfer 协议；本电池为 **append-then-ask 压测**，指标不可直接对比。结构层价值仍在 session 路由 + 门控 + 平坦传输，非 benchmark 百分点的强行对齐。
