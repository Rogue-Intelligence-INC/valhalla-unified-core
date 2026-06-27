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

## 4. v2 代数门控（E7 整数，无拟合 float）

**参数（代数整数）：** r=7，δ=5，dim=133，base=dim+δ=138

| 量 | 公式 | 有理数形式 |
|----|------|------------|
| 绝对阈值 | τ(k) = (r+δ)/(dim+δ+k) | **12/(138+k)** |
| 相对 margin | Δ_req(s₁) = s₁·δ/(dim+r) | **s₁·5/140 = s₁/28** |
| 结构门 | cycles ≥ 2 | C_min = 2 |

**emit 条件：**

```
emit ⟺ cycles ≥ 2
     ∧ s₁ ≥ 12/(138+k)
     ∧ (s₁ − s₂) ≥ s₁·5/140
     ∧ ¬native_reject
```

Rust：`native_qa.rs` 导出 `fog_evidence`（native s₁,s₂）+ `fog_decision`；`ValhallaBaseRow` 透传。

Python：`fog_gate.py` · 协议 `fate-output-gate-v2`

### v2 首轮结果（2026-06-27）

| 模式 | G1 always | emitted precision | coverage |
|------|-----------|-------------------|----------|
| v1_fixed (0.12/0.03) | 96.8% | 96.6% | 93.5% |
| **v2_algebraic** | 96.8% | **96.6%** | **93.5%** |
| v2_rust_native | 96.8% | 96.6% | 93.5% |

**Verdict:** `FOG_V2_ALGEBRAIC_OK` — 与 v1 等效精度/覆盖，但阈值 **全由 E7 整数导出**（138=base_α，12=r+δ）。

---

## 5. v1 实现（benchmark 层，已 superseded by v2）

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
3. **v3** — idle proactive trigger + self-probe ✅ `proactive-fate-v2` · PPI-v2=**0.930** · UP=**100%** · MAR=**88.9%**

```bash
python3 tools/valhalla_inference/test_proactive_fate_v2.py
```

报告：`reports/valhalla_inference/PROACTIVE_FATE_V2_REPORT.md`
