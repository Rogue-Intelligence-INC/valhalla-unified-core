# Valhalla 推理栈 — 日结 2026-06-30

**主题：** E7 代数接入 Fate · 长久记忆结构学习 · Proactive Fate v2 全绿 · 全量测试

---

## 1. 代码（hub-f64）

| 模块 | 变更 |
|------|------|
| **`e7_algebra.rs`** | E7 整数推导：τ(k)=12/(138+k)，Δ=s₁·5/140，affinity±，QA 强度 |
| **`native_qa.rs`** | open structure weight；corpus line affinity rerank；FOG open abstain（保留 `[corpus:N]` citation） |
| **`signal_ingress.rs`** | `corpus_line_affinity` snapshot；`apply_corpus_retrieval_feedback`（Q↔line grinder + 代数 delta） |
| **`valhalla_base.rs`** | QA 反馈 wiring；proactive 探针：GDP 缩写、单数字 token；Fate line structural feedback |
| **`lib.rs`** | `feedback_corpus_line_structural`；QA 强度改代数 |

**哲学：** 结构优先、不确定 abstain、不硬编码 WH/continent 规则表凑分。

---

## 2. 测试与指标

| 协议 | 脚本 | 结果 |
|------|------|------|
| long-memory-v1 (4 arms) | `test_long_memory_v1.py` | **73/76 (96.0%)** production |
| fate-algebra-corpus-v1 | `test_fate_algebra_corpus_v1.py` | **PASS** τ/Δ Rust↔Python |
| external-holdout-v1 | `test_external_holdout.py` | **15/15 (100%)** |
| fate-output-gate-v2 | `test_fate_output_gate.py` | G1 87.1% · prec 100% · FOG_V2_NEEDS_TUNING (coverage) |
| proactive-fate-v2 | `test_proactive_fate_v2.py` | **72/72 (100%)** · PPI-v2 **0.921** |
| 全量 inference (24 scripts) | `test_*.py` ×24 | **23→24 PASS**（proactive v2 修复后） |

### Proactive v2 修复（1234）

1. Exit：PPI≥0.75 + gates + FIR 为主，不再与 STRONG verdict 冲突  
2. Fair aligned：`targeted_context` + `emit_grounded_or_defer`  
3. 探针：GDP↔Gross Domestic Product、单数字 `2`  
4. Fair 第 3 轮 warmup（spread 门控，不降 E7 阈值）

---

## 3. Env（新增/常用）

| 变量 | 默认 | 说明 |
|------|------|------|
| `VALHALLA_OPEN_STRUCTURE_WEIGHT` | 1.2 | open rerank 结构项 |
| `VALHALLA_CORPUS_LINE_AFFINITY_WEIGHT` | 0 | rerank；`algebra`/`tau` 启用 τ(k) |
| `VALHALLA_OPEN_FOG_ENFORCE` | true | open 无 citation 时 FOG abstain |
| `VALHALLA_CORPUS_AFFINITY_POS/NEG` | τ(0)·align / δ/(dim+r)·align | 可 env 覆盖 |

---

## 4. 文档

- `reports/valhalla_inference/LONG_MEMORY_OPTIMIZATION_20260628.md`
- `reports/valhalla_inference/PROACTIVE_FATE_V2_REPORT.md`
- VUC：`valhalla-unified-core/docs/FATE_E7_ALGEBRA_AND_MEMORY.md`
- 索引：`docs/README.md` · VUC `README.md`

---

## 5. 复现

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_long_memory_v1.py --arm production
python3 tools/valhalla_inference/test_fate_algebra_corpus_v1.py
python3 tools/valhalla_inference/test_proactive_fate_v2.py
python3 tools/valhalla_inference/test_external_holdout.py
```

---

## 8. 公认 Benchmark 全量跑完 (2026-06-30)

| Benchmark | 结果 |
|-----------|------|
| RAGTruth | **40/40** grounded |
| Needle @ depth 30 | **4/4** |
| LongBench-v2 | **7/20 (35%)** |
| Scaling open targeted | **31/31** · +6.5pp @0.5B |
| Scaling MCQ | **65% vs 15%** @0.5B |
| **MCQ ladder (Qwen lm_patch)** | **0.5B 70% → 3B 100%** (n=10) |
| Backbone universality | 87% (corpus) / **100%** (targeted) |
| External holdout | **15/15** |

**实验总结：** [`EXPERIMENT_SUMMARY_20260630.md`](../reports/valhalla_inference/EXPERIMENT_SUMMARY_20260630.md)

```bash
python3 tools/valhalla_inference/run_recognized_benchmarks.py
```

---

## 7. 多 backbone 规模化 & 0→1 训练

| 发现 | 数据 |
|------|------|
| 结构 open **backbone 无关** | Valhalla **31/31** @ targeted |
| 小模型 **结构溢价** | 0.5B: **+6.5pp** vs trad RAG |
| 同 scale **MCQ hybrid** | 0.5B: **65% vs 15% (+50pp)** |
| **零权重 transfer** | 87.1% · **+38.7pp** vs polluted |
| **MCQ ladder Qwen** | 0.5B **70%** → 3B **100%** · slope +0.39/log₁₀(params) |
| TPI-v2 | **0.755** |

详见 [`MODEL_SCALING_20260630.md`](../reports/valhalla_inference/MODEL_SCALING_20260630.md) · [`MCQ_LADDER_20260630.md`](../reports/valhalla_inference/MCQ_LADDER_20260630.md)

---

## 6. Qwen 分片 lm_patch ladder (2026-06-30)

- **`patch_lm.rs`**：`model.safetensors.index.json` + 多分片加载（3B/7B）
- **`test_mcq_ladder_v1.py`**：`mcq-ladder-v1` · Qwen 0.5B / 3B / 7B
- **结果：** 0.5B **7/10** → 3B **10/10** · verdict `MCQ_LADDER_SCALES`
- **7B：** 未下载；log-linear 投影 ~100%

```bash
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
python3 tools/valhalla_inference/test_mcq_ladder_v1.py --fast
python3 tools/valhalla_inference/download_backbone_models.py --only qwen --with-7b  # optional
```

---

*Rogue Intelligence LNC. · Valhalla monorepo · 2026-06-30*
