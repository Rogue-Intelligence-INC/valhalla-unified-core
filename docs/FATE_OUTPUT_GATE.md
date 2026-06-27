# Fate Output Gate (FOG) — 何时输出

> **Protocol:** `fate-output-gate-v1`  
> **Status:** Design + benchmark · **Updated:** 2026-06-27  
> **Test:** `tools/valhalla_inference/test_fate_output_gate.py`

---

## 1. 问题

当前 ValhallaBase 路径：**有输入就 decode**。Native 层虽有 `open_reject_low_score`，但：

- 不是 Fate 级统一门控
- incubation 固定 cycle 数，非 closure 驱动
- 无 **defer**（继续孵化）与 **主动输出** 分流

FOG 目标：**Fate 判断「现在配不配说」**，而非决定「说什么」。

---

## 2. 三道门（合取）

```
emit ⇐ StructureReady ∧ EvidenceReady ∧ TriggerPresent
```

| 门 | 信号（已有） | 未过 → |
|----|-------------|--------|
| **StructureReady** | `incubation_cycles ≥ min`；Tile/Stem converged；`detect_convergence_pattern` ∈ {fixed_point, converging} | `defer` |
| **EvidenceReady** | `top_score ≥ τ`；`margin = top₁−top₂ ≥ δ`；非 `open_reject_*` | `abstain` |
| **TriggerPresent** | 用户 question；或 idle/probe 主动触发（v2） | 无输出 |

**原则：** diverging / 低 margin → 闭嘴，继续 ingest 或 incubate。

---

## 3. 与现有代码对应

| 组件 | 位置 |
|------|------|
| Native abstain | `native_qa.rs` · `min_retrieval_score` · `open_reject_low_score` |
| Fate 收敛 | `fate-f64` · `detect_convergence_pattern` · `has_fate_converged` |
| Telemetry | `valhalla_base.rs` · `FateTelemetry` · `hub_prefs_spread` |
| QA feedback | `apply_qa_feedback` · **输出后**；FOG v2 可反馈调 τ |

生产默认 `quad_cycle` 下 spread 常为 0 → **StructureReady 首版绑 incubation_cycles + native reject**。

---

## 4. v1 实现（benchmark 层）

Python `fog_gate.py` 在 ValhallaBase 响应之上做 **后验门控**（与 future Rust 内嵌 FOG 同逻辑）：

- `defer`：`incubation_cycles < min_structure_cycles`
- `abstain`：native reject / `top_score < τ` / `margin < δ`
- `emit`：否则放行 baseline answer

---

## 5. 证伪条件

| 失败 | 含义 |
|------|------|
| FOG emitted precision ≤ always-emit accuracy | 门控无质量增益 |
| distractor 上 abstain 率不升 | margin 无效 |
| targeted 上 emit 率 < 80% | τ/δ 过严 |

---

## 6. 复现

```bash
python3 tools/valhalla_inference/test_fate_output_gate.py
```

报告：`reports/valhalla_inference/fate_output_gate_test.json`

---

## 7. 路线图

1. **v1（本文件）** — 反应式 FOG benchmark（Python）
2. **v2** — Rust `ValhallaBaseRow.fate_output_gate` + `top_matches` margin
3. **v3** — idle proactive trigger + self-probe
