# Stem 组织 / Tile 聚合 — 机制与实测有效性分析

**Date:** 2026-06-28  
**Scope:** Stem `stem_organ_clusters`、Tile `completed_tiles` 是否在运行时形成，是否进入生产路径并 measurable 起效  
**Status:** Analysis record（非新 benchmark run；综合既有实验 + 源码路径）

---

## 1. Executive summary

| 维度 | Stem「组织」 | Tile「聚合」 | 能否实际起效 |
|------|-------------|-------------|-------------|
| **代码上是否发生** | ✅ | ✅ | 机制真实存在 |
| **生物学隐喻是否成立** | ⚠️ 弱（多为 1 mega-cluster） | ⚠️ 部分（merge/层状，非完整 NN） | 结构有，功能器官未分化 |
| **Native 检索 / MCQ** | modest 增益 | **略强于 Stem** | persistent incubation 下可见 |
| **生产 Hybrid 栈** | 间接（patch / routing） | 间接（tile_fate 轨道） | **Open 强；MCQ 不靠纯结构** |

**一句话：** Stem 与 Tile 都会在运行时形成可度量的中间结构，并进入 `score_structure_alignment` 影响 native 记忆排序；在当前 fair-1.2 规模语料下，主要杠杆是 **persistent incubation + 结构余弦加权**，而非「多器官 / 多 Tile 语义模块」本身。生产 MCQ 主路径为 **lm_patch（65.2%）**；纯 structure 仅 **30.4%**。

---

## 2. Stem 是否形成「组织」？

### 2.1 机制

- **源码:** `manifestsys/hub-f64/src/signal_ingress.rs` → `build_stem_organ_clusters`
- **算法:** 细胞连接图 BFS 连通分量；边权 `> 0.01`；簇内 `cell_count ≥ min_cells`（默认 2，env `VALHALLA_STEM_ORGAN_MIN_CELLS`）
- **导出:** `stem_cluster_signatures` + `stem_cluster_energies` → `ValhallaModelPatch`
- **打分:** `native_qa.rs` → `score_structure_alignment` — organ cluster 权重 **0.12**（单细胞 **0.08**）

### 2.2 实测形态

| 场景 | 细胞数 | organ clusters | 解读 |
|------|--------|----------------|------|
| 早期 1K 分析 (`STEMCELL_TILE_STRUCTURE_ANALYSIS_20260128.md`) | — | **0/4** 预期器官 | 特化率 0.6%，胚胎期 |
| fair MCQ stemcell persistent | **~159** | **1** | 整图常合并为 **1 个 mega-cluster** |
| multimodal smoke (`potential_smoke.json`) | 64 | 1（210 internal edges） | 单簇占满细胞图 |
| tile-only body | 0 | 0 | 不建 stem 组织 |

### 2.3 判断

- **工程上算「组织」：** 连通簇 + 簇签名 + 检索加权 ✅  
- **功能分化器官（感知/记忆/协调等）：** 当前小语料下 **未形成** ❌  

---

## 3. Tile 是否形成「聚合」？

### 3.1 机制

- **源码:** `manifestsys/tile-quattro/src/tile_complete.rs`
- **循环:** `process_tiles_cycle()` → `execute_cluster_merge`（合并）+ 高能量分裂 + 低能量死亡
- **导出:** `completed_tiles` → enriched signature（mean, variance, activation, conn_norm）
- **打分:** `score_structure_alignment` — tile 权重 **0.15** × energy × activation

### 3.2 实测形态

| 场景 | completed tiles | 备注 |
|------|-----------------|------|
| 结构分析 1K 数据 | ~63 → merge ~33% | 层状方差分布 |
| fair MCQ tile persistent（49 行语料） | **~10–11** | `tile_connections > 0` |
| stem-only body | **0** | 无 Tile 聚合 |

### 3.3 判断

**聚合确实发生**（micro → completed，merge 减 Tile 数）；语料规模下为 **粗粒度聚类**（~11 Tile），非大规模语义模块。

---

## 4. 能否实际起效？（分路径）

### 4.1 Native 结构解码（mcq_option / structure_fate）

**实验:** `TILE_STEM_WHOLE_QUESTION_20260622_0249` — 整题 persistent，一次 incubation + 46 MCQ sequential QA

| Body | MCQ | vs isolated 28.3% |
|------|-----|-------------------|
| **tile** | **22/46 (47.8%)** | **+19.6 pp** |
| **stemcell** | **19/46 (41.3%)** | **+13.0 pp** |
| isolated baseline | 13/46 (28.3%) | — |

145Q 全量 persistent：tile **41.4%** vs stem **37.9%** vs isolated **34.5%**。

**要点:**
- **Persistent incubation** 是最大杠杆（结构在 session 累积）
- **Tile > Stem** 于纯 native MCQ
- Open native 仍弱（~23–26%），远低于生产 Hybrid **96.8%**

### 4.2 Parallel / Triad 融合（负结果）

**实验:** `TILE_STEM_PARALLEL_20260621_2320` — tile×0.5 + stem×0.5 patch，`mcq_parallel`

| Body | MCQ |
|------|-----|
| tile isolated | 30.4% |
| stem isolated | 28.3% |
| parallel / triad | **28.3%** |

简单等权融合 **无增益**。

### 4.3 Hybrid 多轨道

| 轨道 | 145Q test | MCQ subset |
|------|-----------|------------|
| `triad_persistent` | 39.31% | — |
| `tile_fate_persistent` | 41.38% | **52.17%** |
| `stemcell_fate_persistent` | 实验 arm | 弱于 tile |

Deploy 选轨：`pick_memory_deploy` — 按 decode_path rank，**无 cross-track 信号 merge**。

### 4.4 生产 ValhallaBase（mcq-coverage-v1）

| Arm | MCQ (n=46) |
|-----|------------|
| **production hybrid lm_patch** | **30/46 (65.2%)** |
| structure_fate / native mcq_option | **14/46 (30.4%)** |
| traditional LM + RAG | 13/46 (28.3%) |
| oracle max(native, patch) | 32/46 (69.6%) |

- 生产 MCQ：**46/46** 走 `lm_patch/fused_mcq_logprob`
- `max_pick` deploy：**65.2%**（+0 pp vs lm_patch）；阈值未触发 native 翻转

**Open 生产栈（96.8%）：** 结构价值主要在 **Triad patch + persistent snapshot + session routing + FOG/token**，`score_structure_alignment` 为记忆排序 secondary boost（0.08–0.15 权重）。

---

## 5. 结构打分权重（源码锚点）

`score_structure_alignment`（`native_qa.rs`）:

| 信号 | 权重因子 |
|------|----------|
| Tile signature | 0.15 × hub_pref × cosine × energy × (1+\|act\|) |
| Stem cell | 0.08 × stem_w × cosine |
| Organ cluster | 0.12 × stem_w × cosine × energy |

主排序仍由 `dot_cosine(memory, query)` + `0.35 × dot_cosine(memory, patch)` 主导。

---

## 6. 证伪标记（预注册诚实边界）

| 标记 | 含义 |
|------|------|
| `STEM_ORGAN_NOT_FUNCTIONALLY_DIFFERENTIATED` | fair 语料下多为 1 mega-cluster，非 4 功能器官 |
| `TILE_AGGREGATION_COARSE_AT_SMALL_CORPUS` | ~11 completed tiles，语义模块感弱 |
| `MCQ_STRUCTURE_BELOW_LM_PATCH` | native/structure_fate 30.4% << lm_patch 65.2% |
| `PARALLEL_TILE_STEM_FUSION_NO_LIFT` | 等权融合 28.3%，不优于单轨 |
| `STRUCTURE_VALUE_IN_SESSION_NOT_RAW_CEILING` | Open 96.8% 靠 routing/session；非 structure-only 26% |

---

## 7. 下一步（工程优先级）

1. **stem-relative MCQ comparator** — 选项直接对 stem/tile 签名比，而非仅 boost 语料行
2. **调高 organ 分化条件** — `VALHALLA_STEM_ORGAN_MIN_CELLS`、更长 incubation、更大语料 → 观测多簇是否提升 oracle 选轨
3. **max_pick 阈值调优** — oracle 69.6% vs deploy 65.2%（~4.3 pp headroom）
4. **勿做** — tile×0.5 + stem×0.5 简单 parallel（已证无效）

---

## 8. 引用实验与源码

| 资产 | 路径 |
|------|------|
| Stem organ 构建 | `manifestsys/hub-f64/src/signal_ingress.rs` |
| 结构对齐打分 | `manifestsys/hub-f64/src/native_qa.rs` |
| Tile merge/split | `manifestsys/tile-quattro/src/tile_complete.rs` |
| Hybrid 选轨 | `manifestsys/hub-f64/src/hybrid.rs` |
| Tile/Stem 整题 persistent | `reports/experiments/TILE_STEM_WHOLE_QUESTION_20260622_0249.json` |
| Parallel 负结果 | `reports/experiments/TILE_STEM_PARALLEL_20260621_2320.json` |
| MCQ coverage | `reports/valhalla_inference/mcq_coverage_test.json` |
| 早期结构分析 | `STEMCELL_TILE_STRUCTURE_ANALYSIS_20260128.md` |
| Hybrid 架构 | `docs/hybrid_2.0/ARCHITECTURE_DETAILED.md` |
