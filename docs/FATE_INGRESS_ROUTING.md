# Fate Ingress Routing — Experiment Summary & Production Default

> **Status:** PRODUCTION_DEFAULT_SET  
> **Protocol:** `fate-weight-ladder-v1`  
> **Default:** `fate_ingress_routing=quad_cycle` (pure average, 4-quad activation per corpus line)  
> **Reports:** `reports/fate_weight_ladder_*.json`

---

## 中文摘要

在 ValhallaBase 高约束 Phase（Fate 路由锁定、`fate_routing_free=false`）下，Hub 如何把 corpus 行信号分配给四象限（BlackHole / MeshBrain / MultiNova / BaseForce）会直接影响：

1. **四系统是否都被激活**
2. **Fate 权重是否分化**（`hub_prefs_spread`）
3. **话题连续性与检索准确率**

我们对比了四种 ingress 模式，结论：

| 模式 | 四 quad 激活 | Fate spread | Phase1 准确率 (15+15) | 结论 |
|------|-------------|-------------|----------------------|------|
| `round_robin` | 长期趋近 25%，单行内可能偏斜 | ~0 | — | 对称但单行不均 |
| `semantic` | 1–2 quad 垄断 (~90%) | ~0.93 | 91.1% | 权重分化但其余 quad 休眠 |
| **`quad_cycle`** | **4/4 各 25%** | **0** | **93.3%** | **✅ 生产默认** |
| `hybrid_quad_semantic` | 4/4，主导 ~42% | ~0.88 | 91.1% | 折中，准确率略低 |

**生产决定：保持纯平均 `quad_cycle`。**  
理由：最高 Phase1/Phase2 准确率；每条 corpus ingest 循环内四象限同时获得均等信号；实现简单、行为可预测。Fate 权重在 Fixed 模式下保持均匀（spread=0），符合当前「高约束探索、四系统协同 ingest」目标。

推荐生产配置见文末。

---

## 1. Background — Why This Matters

ValhallaBase v1 runs a **Triad session** (Hub + Tile + StemCell + Fate) over a growing corpus. Each corpus line is ground into port signals; Hub routes each signal to one of four meta-systems:

| Index | Quad | Typical semantic bucket |
|-------|------|-------------------------|
| 0 | BlackHole | physics, force, energy |
| 1 | MeshBrain | language, text, symbols |
| 2 | MultiNova | process, chemistry, phase change |
| 3 | BaseForce | geography, capitals, locations |

When `fate_routing_free=false` (high constraint), Hub routing is **locked** — ingress mode decides load shape. Tile and StemCell always receive parallel signals regardless of quad routing.

### Problem discovered (Fate ladder 200 rounds)

Original high-constraint setup used **global round-robin** → symmetric `hub_routed` → uniform `hub_prefs` `[0.25×4]` → **Fate never differentiated** (`spread=0`).

We then tried **semantic winner-take-all** → spread rose to ~0.99 but **only 1–2 quads activated** per topic thread (e.g. physics: BH 2944, MB/MN 0).

**Goal:** activate all four quads while maintaining answer quality.

---

## 2. Ingress Modes Implemented

### 2.1 `round_robin` (legacy)

- Route by `total_requests % 4` globally.
- Long-run ~25% each; **within a single corpus line** all 32 hub signals may hit the same quad.

### 2.2 `semantic`

- One quad per corpus line via keyword scoring (`route_corpus_line_semantic`).
- All signals from that line → same quad.
- **Effect:** strong topic→quad mapping; 2/4 quads active; prefs skew ~99% to dominant quad.

### 2.3 `quad_cycle` ✅ **Production default**

- **Per corpus line:** reset counter; signal `i` → quad `i % 4`.
- 32 signals/line → **8 per quad (25% each)** every ingest loop.
- **Effect:** `balance_score=1.00`, all 4 quads active; `hub_prefs_spread=0` under Fixed Fate weights (symmetric).

```rust
// manifestsys/hub-f64/src/lib.rs — simplified
IngressRoutingMode::QuadCycle => {
    let idx = self.ingress_line_signal_idx;
    self.ingress_line_signal_idx += 1;
    Self::quad_from_index(idx)  // BH → MB → MN → BF → …
}
```

### 2.4 `hybrid_quad_semantic` (experimental)

- Even signals → quad cycle; odd signals → semantic primary quad.
- ~50% balanced + ~50% semantic boost to topic quad.
- **Effect:** 4/4 active, spread ~0.88, dominant quad ~42%; accuracy matches semantic, below quad_cycle.

---

## 3. Benchmark Design

**Script:** `tools/valhalla_inference/test_fate_weight_ladder_200.py`

| Parameter | Quick compare | Full ladder |
|-----------|---------------|-------------|
| Phase 1 | 15 rounds | 100 rounds |
| Phase 2 | 15 rounds | 100 rounds |
| Threads | physics, chemistry, australia | same |
| Constraint | 1.0 → 0.55 (P1), 0.55 → 0 (P2) | same |

**Phase 1 (high constraint):** `fate_weight_mode=fixed`, `fate_routing_free=false`, ingress mode as configured.  
**Phase 2 (release):** gradually `evaluated` weights, `fate_routing_free=true`, ingress → `round_robin`.

**Metrics:**

- `on_topic_rate` — answer contains hint, excludes forbidden terms
- `hub_prefs_spread` — max−min of Fate affinity vector
- `quad_balance` — share spread across 4 quads (`balance_score=1.0` = perfectly even)

---

## 4. Results

### 4.1 Three-mode comparison (15+15 × 3 threads = 45 rounds/phase aggregate)

| Mode | Phase1 acc | Phase2 acc | P1 spread | Avg balance |
|------|-----------|-----------|-----------|-------------|
| **quad_cycle** | **93.3%** (42/45) | **80.0%** (36/45) | 0.000 | **1.00** |
| semantic | 91.1% (41/45) | 77.8% (35/45) | 0.930 | 0.51 |
| hybrid_quad_semantic | 91.1% (41/45) | 77.8% (35/45) | 0.879 | 0.75 |

**Phase2 accuracy drop (~−13pp)** appears across all modes — tied to constraint release + evaluated routing, not ingress mode alone.

### 4.2 quad_cycle — final quad shares (all threads)

```
BlackHole  25% | MeshBrain  25% | MultiNova  25% | BaseForce  25%
active_quads = 4/4 every thread
```

### 4.3 semantic — final quad shares (example)

```
physics:   BH 59% / MB 11% / MN 14% / BF 16%
chemistry: MN 61% / others ~11–16%
australia: BF 61% / others ~11–16%
```

### 4.4 Full 200-round semantic ladder (earlier run)

- Phase1: 243/300 (81.0%), spread=0.989
- Phase2: 192/300 (64.0%), spread=0.994
- Confirmed semantic achieves spread but monopolizes one quad per topic.

---

## 5. Architecture Decisions

### ✅ Adopted: `quad_cycle` as default

| Criterion | quad_cycle |
|-----------|------------|
| Four-quad activation | ✅ Every corpus line |
| Answer quality | ✅ Best in quick compare |
| Predictability | ✅ Deterministic 25% split |
| Fate differentiation | ❌ spread=0 (acceptable for current Fixed high-constraint phase) |
| Code path | `emit_body_ports_with_line` → Hub `ingress_line_signal_idx` |

### Deferred: `hybrid_quad_semantic`

- Use when Fate weight differentiation **and** quad activation are both required.
- Trade-off: −2.2pp Phase1 vs quad_cycle.

### Deferred: `semantic`

- Use for topic-specialized Fate exploration experiments only.
- Not for production context-flexibility path.

---

## 6. Production Configuration

```python
from valhalla_base import ValhallaBase

base = ValhallaBase(
    decode="hybrid",
    follow_up_decode="native_follow_up_aware",
    fate_weight_mode="fixed",           # high constraint
    fate_routing_free=False,            # locked Fate routing in explore phase
    fate_ingress_routing="quad_cycle",  # ✅ default — pure average per line
    incubation_cycles=2,
)
```

**JSON config (`valhalla-base-v1`):**

```json
{
  "config": {
    "decode": "hybrid",
    "follow_up_decode": "native_follow_up_aware",
    "fate_weight_mode": "fixed",
    "fate_routing_free": false,
    "fate_ingress_routing": "quad_cycle"
  }
}
```

**Response features when active:** `fate_ingress_quad_cycle`

---

## 7. Code Locations (Valhalla monorepo)

| Component | Path |
|-----------|------|
| Ingress modes enum | `manifestsys/hub-f64/src/lib.rs` — `IngressRoutingMode` |
| Per-line quad cycle | `ValhallaHub::route_request`, `ingress_line_signal_idx` |
| Corpus line wiring | `signal_ingress.rs` — `emit_body_ports_with_line` |
| Config / telemetry | `valhalla_base.rs` — `ValhallaFateIngressRouting` |
| Python API | `tools/valhalla_inference/valhalla_base.py` |
| Benchmark | `tools/valhalla_inference/test_fate_weight_ladder_200.py` |

---

## 8. Reproduce

```bash
cd /path/to/Valhalla
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base

# Default quad_cycle (15+15 quick)
python3 tools/valhalla_inference/test_fate_weight_ladder_200.py

# Compare all three modes
python3 tools/valhalla_inference/test_fate_weight_ladder_200.py --compare-all

# Full 200-round ladder
python3 tools/valhalla_inference/test_fate_weight_ladder_200.py --phase1 100 --phase2 100
```

---

## 9. Related Documents

- [CONTEXT_FLEXIBILITY_MAX_GOAL.md](./CONTEXT_FLEXIBILITY_MAX_GOAL.md) — primary product target for session context
- [INTRODUCTION.md](./INTRODUCTION.md) — VUC architecture overview
- Monorepo reports: `reports/valhalla_inference/fate_weight_ladder_*.json`

---

## 10. Next Steps (optional)

1. **Phase2 accuracy gap** — investigate constraint release independent of ingress mode (−13pp common to all modes).
2. **Evaluated + quad_cycle** — whether spread can emerge when `fate_weight_mode=evaluated` with symmetric ingress.
3. **Retrieval coupling** — whether quad-specific Tile/Stem specialization should mirror Hub routing (currently decoupled).

---

*Last updated: 2026-06-19 · Rogue Intelligence LNC*
