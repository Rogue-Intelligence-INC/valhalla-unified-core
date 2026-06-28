# Valhalla Unified Core — 独特点总览与详细介绍

> **Version:** 1.0 · **Date:** 2026-06-27  
> **配套论文:** `papers/ValhallaBase_Distinctive_Inference_Paradigm.tex`  
> **实验汇总:** `reports/valhalla_inference/CONFIDENCE_REPORT_v1.md`

---

## 0. 是否该用 Token 计算来佐证能力？

**结论：应该用，但要用对维度——不是「少 token = 更聪明」，而是「同等准确率下，结构层改变了 context 的承载与传输成本」。**

### 建议纳入文档的三类 Token / 成本指标

| 指标 | Valhalla 测法 | 传统 RAG / 纯 LM 对照 | 已有数据 |
|------|---------------|----------------------|----------|
| **Wire 传输成本** | session `append` 每步 payload 字符数 | 每轮重发全 corpus block | **~64 chars/步** vs 终态 **752 chars（3.62×）** · 协议 `context-flexibility-max-goal-v1` |
| **LM prefill tokens** | hybrid open 路径：corpus 不进 prompt，仅 question + patch | 同题 RAG：corpus 全文进 prompt | 待补 `token-efficiency-v1`（见 §8） |
| **Decode tokens** | native 检索路径：0 生成 token（结构输出） | LM 开放题生成 128+ tokens | 按路径分列报告 |

### 不应做的表述

- ❌ 用 token 数替代准确率（准确率仍用 Wilson 区间，见 confidence report）
- ❌ 声称「零 token 推理」（patch LM 路径仍有 prefill + decode）
- ❌ 只报 chars 不换算 tokenizer（对外需统一用 Qwen tokenizer 计 prefill）

### 推荐对外叙事

> **Valhalla 在 fair holdout 上与 Qwen2.5-0.5B RAG 统计打平（96.8%），但 session 内 context 增量传输 ~64 chars/步，传统全 prompt 终态 ~752 chars；结构优势体现在路由、门控与 multimodal 非隔离，而非 raw RAG ceiling。**

---

## 1. 独特点一览（12 项）

| # | 独特点 | 一句话 | 可证伪？ |
|---|--------|--------|----------|
| D1 | **结构先行、LM 作头** | Triad 孵化快照后再 decode，非 prompt=RAG | ✅ universal core 107 任务 |
| D2 | **零权重 session 学习** | 无 SGD/LoRA，定向 ingest + snapshot | ✅ TPI-v2 / NPPI |
| D3 | **Hybrid 题型路由** | open→native，MCQ→lm_patch logprob | ✅ fair-1.2 分 slice |
| D4 | **Session 路由 vs 污染** | transfer fresh +61pp vs polluted dump | ✅ paired bootstrap |
| D5 | **Context 灵活追加** | 内部 context 线性增，wire ~flat/step | ✅ growth curve |
| D6 | **Follow-up-aware 检索** | question_history 加权，30 轮 96.7% on-topic | ✅ context-drift-v2 |
| D7 | **FOG 代数输出门** | E7 整数 τ，emit/abstain/defer | ✅ FOG-v2 96.6% precision |
| D8 | **Proactive Fate 主动** | idle 自探针 + 门控 nudge，UP 100% | ✅ proactive-v2 |
| D9 | **跨语言同核** | EN/ZH/FR 同 corpus line，无 language_switch | ✅ CCU 0.950 |
| D10 | **Multimodal 非隔离** | 单 session 脉冲 vs 后融合 | ✅ 0.964 vs 0.943 |
| D11 | **可审计路由** | 每答记录 decode_path / routing_source | ✅ JSON 产物字段 |
| D12 | **代数 E7 协调** | spread gate τ=12/138，hub_prefs | ✅ FOG + proactive |

---

## 2. 详细介绍

### D1 — 结构先行，LM 仅作 Decode 头

**问题：** Transformer 把「记忆」和「生成」绑在同一 weight 矩阵；换 domain 要么全量微调，要么把 corpus 塞进 prompt。

**Valhalla 做法：** Hub / Tile / StemCell / Fate 在 **TriadIncubationSnapshot** 中完成结构凝结；Qwen2.5-0.5B 仅作 runtime patch 或 MCQ logprob 头。开放题默认 **native 结构检索**，不依赖 LM 幻觉生成。

**证据：** non-isolated universal core 107 任务 avg **0.964**；open_retrieval hybrid **96.8%** [83.8%, 99.4%]。

**与 RAG 区别：** RAG 检索的是 **文本块**；Valhalla 检索的是 **孵化后的结构记忆 + corpus index**，LM 读的是 patch 后的 snapshot。

---

### D2 — 零权重 Session 学习（推理时范式）

**问题：** 垂直领域知识更新通常需要 fine-tune 或 LoRA 循环。

**Valhalla 做法：** `merge_context` / targeted ingest → incubation → per-question eval；**不更新 LM 权重**。可选 `fate_qa_feedback` 闭环调 Fate 质量，仍非梯度训练。

**证据：**
- TPI-v2 = **0.790** [0.740, 0.823]
- B1 语料 10%→100%：准确率 **100%→96.8%**（数据高效）
- 证伪标记：`NOT_WEIGHT_FINE_TUNE_REPLACEMENT`、`SESSION_SNAPSHOT_NO_HOLDOUT_LIFT_BEYOND_RAG`

**诚实边界：** holdout 上 cold RAG = transfer = **96.8%**；session 价值在 **避免污染**（+61pp），不在 snapshot 额外记忆。

---

### D3 — Hybrid 题型感知路由

**问题：** 开放题、MCQ、数值题失败模式不同，单一 decode 路径次优。

**Valhalla 做法：**

```python
ValhallaBase(decode="hybrid", follow_up_decode="native_follow_up_aware")
```

| 题型 | 路由 | fair 表现 |
|------|------|-----------|
| open_retrieval | native | 96.8% |
| MCQ | lm_patch logprob | lm_patch 100% vs hybrid 96.8% |
| numeric | max(structure, patch) | hybrid 80.69% 总集 |

**独特点：** 用户无感切换；JSON 响应含 `decode_path` 可审计。

---

### D4 — Session 路由：Transfer 救援污染 Session

**问题：** 把 80+ 行 corpus 全 dump 进 session 再 batch eval → **35.5%**（检索污染）。

**Valhalla 做法：** eval 时 **清空 corpus → per-question targeted append** → transfer eval。

**证据：** polluted **35.5%** → transfer **96.8%**，lift **+61.3pp** [+45.2, +77.4]（paired n=31）。

**生产含义：** Session 是有价值的，但必须 **fresh retrieval 协议**，不能当「越大越好」的 prompt。

---

### D5 — Context 传输：~64 chars/步 vs 全 prompt 重发

（见 token-efficiency-v1：wire **0.16×** · prefill **0.29×** @ 96.8% holdout）

---

### D13 — MCQ 专项覆盖 + max_pick 路由

**问题：** MCQ 是相对 open（96.8%）的已知短板；结构 `mcq_option` ~30%，纯 LM RAG ~28%。

**Valhalla 做法：** 生产默认 `mcq_decode=lm_patch`（**65.2%**）；新增 `mcq_decode=max_pick` deploy 双轨 pick。

**证据：** mcq-coverage-v1 · vs trad_lm **+37pp** · oracle ceiling 69.6%

---

### D6 — Follow-up-aware 多轮检索

**问题：** 多轮对话中，后续问题应继承话题但不被旧关键词绑架。

**Valhalla 做法：** Rust `native_qa.rs` 中 `follow_up_retrieval_boost()`：当前问句关键词加权、旧问惩罚、recency bias。

**证据：** extended 30-turn on-topic **96.7%** [83.3%, 99.4%]；swap fidelity **100%**。

---

### D7 — FOG（Fate Output Gate）代数门控

**问题：** 「有输入就 decode」无法 abstain / defer；低置信幻觉无统一 Fate 级拦截。

**Valhalla 做法：** 三道合取门 StructureReady ∧ EvidenceReady ∧ TriggerPresent；v2 用 E7 整数 **τ=12/(138+k)**，Δ≥s₁/28。

**证据：** emitted precision **96.6%** [82.8%, 99.4%]；distractor abstain **58.3%**；coverage **93.5%**。

**哲学：** Fate 决定 **「配不配说」**，不决定 **「说什么」**（与 native QA 内容解耦）。

---

### D8 — Proactive Fate（主动但未 unsolicited 乱跑）

**问题：** 主动助手易幻觉打断；纯被动无法在长 idle 后延续话题。

**Valhalla 做法：** `proactive_idle` → max-overlap 自探针 → FOG 门控 → grounded nudge；CJK bigram + 中文 probe 模板。

**证据：** UP_on_topic|**emit** **100%** [87.5%, 100%]；MAR **88.2%**；FIR **0%**（mismatch 零幻觉 emit）；PPI-v2 **0.875**。

---

### D9 — 跨语言同核（无 language_switch）

**问题：** 多语言产品常切 embedding 或换模型。

**Valhalla 做法：** 单 canonical corpus line；EN/ZH/FR query 同一 production 栈，`language_switch=false`。

**证据：** CCU **0.950**，core_unified **6/6**；external holdout **15/15 (100%)** [79.6%, 100%]。

---

### D10 — Multimodal 非隔离 Universal Core

**问题：** 典型 multimodal 为 late fusion，同任务跨模态 patch 不对齐。

**Valhalla 做法：** 单 session 内 text→TTS→image 脉冲交错；Fate patch 导出对齐。

**证据：** shared patch pairwise **~1.00**（non-isolated）vs **~0.85**（isolated）；107 任务 non-isolated **100% wins**。

---

### D11 — 可审计产品路由

**问题：** 黑盒 LLM 无法满足政企合规「每答可追溯」。

**Valhalla 做法：** 每条 JSON 响应含 routing metadata（decode_path, fog_decision, proactive_trigger 等）；hybrid deploy 无 oracle。

**证据：** fair-1.2 / confidence 全部 JSON 产物可第三方 replay。

---

### D12 — E7-φ 代数协调层

**问题：** 多子系统协调常靠 learned gating 或手工 if-else。

**Valhalla 做法：** spread gate **τ(0)=12/138**，δ/(dim+r) 缩放；proactive / FOG / hub_prefs 共用代数信号，非拟合 float。

**与 s-wind 理论线一致：** Φ²=Φ+1 公理派生参数进入 **运行时门控**，非装饰性命名。

---

## 3. 与 Transformer / RAG 对照表

| 维度 | Transformer + RAG | ValhallaBase |
|------|-------------------|--------------|
| 知识更新 | Fine-tune / LoRA | Targeted ingest + snapshot |
| Context 载体 | Prompt tokens | TriadIncubationSnapshot |
| 多轮成本 | 全 history 重 prefill | ~64 chars/step append |
| 输出门控 | 无统一 abstain | FOG 代数三门 |
| 主动对话 | 纯 prompt 驱动 | Proactive idle + overlap gate |
| 跨语言 | 常换 adapter | 同 corpus core unified |
| 多模态 | Late fusion | Non-isolated session pulses |
| 审计 | 黑盒 logprob | Per-answer routing JSON |

---

## 4. 当前 headline 数字（confidence-report-v1.1）

| 域 | 指标 | 点估计 | 95% CI |
|----|------|--------|--------|
| Grounding | fair_holdout_cold_rag | 96.8% | [83.8%, 99.4%] |
| Routing | transfer_vs_polluted | +61.3pp | [+45.2, +77.4] |
| vs LM | traditional_lm_rag | 96.8% | [83.8%, 99.4%] |
| Quality | fog_emitted_precision | 96.6% | [82.8%, 99.4%] |
| Proactive | UP_on_topic_given_emit | 100% | [87.5%, 100%] |
| Crosslang | crosslang_accuracy | 100% | [82.4%, 100%] |
| External | external_holdout | 100% | [79.6%, 100%] |
| Local corpus | cold_targeted | 100% | [83.9%, 100%] |
| Dialogue | 30turn_on_topic | 96.7% | [83.3%, 99.4%] |
| MCQ lm_patch | mcq_hybrid_deploy | 65.2% | [50.8%, 77.3%] |
| Structure-only MCQ | native/structure_fate | 30.4% | [19.1%, 44.8%] |

---

## 5. Token Efficiency（token-efficiency-v1）

```bash
python3 tools/valhalla_inference/test_token_efficiency.py
python3 tools/valhalla_inference/test_token_efficiency.py --run-valhalla
python3 tools/valhalla_inference/run_confidence_report.py
```

**输出字段：**
- `prefill_tokens_cumulative`（每架构每轮累加）
- `wire_chars_cumulative`
- `holdout_accuracy`（TPI-v2 交叉引用）
- `summary_table`（wire + prefill + decode + accuracy 四列）

报告：`reports/valhalla_inference/token_efficiency_test.json` · wire **0.16×** · prefill **0.29×** @ 96.8% holdout

---

## 6. Stem / Tile 结构诚实评估（2026-06-28）

**问题：** Stem 是否形成「组织」？Tile 是否形成「聚合」？这些结构在生产栈里是否 **实际起效**？

**结论摘要：**

| 子系统 | 形成？ | 生产起效？ |
|--------|--------|-----------|
| Stem `stem_organ_clusters` | ✅ BFS 连通簇 + 簇签名 | ⚠️ native 检索 secondary boost；MCQ 非主路径 |
| Tile `completed_tiles` | ✅ merge/split 聚合 | ⚠️ tile_fate 轨 MCQ **52%**；persistent **+19.6pp** |
| 生物学「4 器官」隐喻 | ❌ fair 语料多为 **1 mega-cluster** | 勿过度声称 |
| Parallel tile+stem 融合 | 机制存在 | ❌ **28.3%**，无增益 |

**证据：**
- Persistent 整题 MCQ：tile **47.8%** vs stem **41.3%** vs isolated **28.3%**（`TILE_STEM_WHOLE_QUESTION`）
- 生产 MCQ：**lm_patch 65.2%** >> structure_fate **30.4%**
- Open **96.8%**：结构经 **Triad patch + session routing + FOG**，非 structure-only（open native ~26%）

**完整分析：** `reports/valhalla_inference/STEM_TILE_ORGAN_AGGREGATION_ANALYSIS_20260628.md` · 实验记录 §16

---

## 7. 文档与论文索引

| 资产 | 路径 |
|------|------|
| 独特点本文 | `docs/DISTINCTIVE_CAPABILITIES_CN.md` |
| Stem/Tile 结构分析 | `reports/valhalla_inference/STEM_TILE_ORGAN_AGGREGATION_ANALYSIS_20260628.md` |
| 推理范式 TeX | `papers/ValhallaBase_Distinctive_Inference_Paradigm.tex` |
| 实验记录 | `docs/EXPERIMENT_RECORD_INFERENCE_PARADIGM.md` |
| Confidence | `reports/valhalla_inference/CONFIDENCE_REPORT_v1.md` |
| Investor one-pager | `docs/INVESTOR_ONE_PAGER.md` |
| Hybrid 145Q 论文（旧） | `papers/memory_hybrid/Hybrid_Structure_Memory_and_Routing.tex` |
