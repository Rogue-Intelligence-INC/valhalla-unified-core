# 有效 Benchmark 解读 — 测了几次 · 对应什么 · 意味着什么 · 因为什么

**Date:** 2026-06-30  
**Stack:** ValhallaBase hybrid · default backbone `Qwen2.5-0.5B-Instruct` · decode `Hybrid`  
**Industry 全量跑分:** 2026-06-30T23:58 UTC（加强下载 + 单轮 industry suite）  
**JSON 索引:** `valid_benchmarks_summary.json` · `industry_benchmarks_summary.json`

---

## 0. 怎么用本文

| 分类 | 含义 | 对外能否引用 |
|------|------|--------------|
| **A · 有效且强** | 数据完整、协议匹配产品能力 | ✅ 可 cite |
| **B · 有效但受限** | 数据真实，分数受 0.5B / 截断 / 协议 cap 约束 | ⚠️ 须说明条件 |
| **C · 无效** | corpus 不满足 benchmark 定义 | ❌ 勿 cite 分数 |

**加强下载（2026-06-30）：** `download_utils.py` — curl + GitHub 镜像链 + `hf-mirror.com` + 磁盘缓存；bundle 刷新 ~16s。  
**复现：** 见文末命令。

---

## 1. Tier A — 有效且可对外引用

### 1.1 RAGTruth（ACL 2024）

| 项 | 内容 |
|----|------|
| **测了几次** | **40Q ×2**（两次独立跑分，结果一致）；**100Q ×1** |
| **结果** | 40/40 (100%) · 100/100 (100%) · abstain **0** |
| **对应什么** | 第三方 RAG **幻觉检测** benchmark：`wandb/RAGTruth-processed` QA 子集；metric = **context-grounded**（回答是否被 ingest 的 context 支持，含 `[corpus:N]` citation） |
| **意味着什么** | ValhallaBase 在「有 corpus、要忠实引用」场景下 **industry 级全绿**；含 50 条带 hallucination label 的参考样本仍 100% grounded |
| **因为什么** | Session **append → Fate 结构检索 → Hybrid decode**；open 路径 FOG abstain + corpus line affinity rerank；不依赖 128K 原生窗口，靠 **ingest 后检索** 定位证据 |
| **报告** | `ragtruth_v1_test.json` · `ragtruth_full_v1_test.json` |

### 1.2 Needle-in-haystack（session 协议）

| 项 | 内容 |
|----|------|
| **测了几次** | **×2**（两次 4/4 一致） |
| **结果** | **4/4 (100%)** @ depth 5 / 10 / 20 / **30**（最深 62 session lines） |
| **对应什么** | 业界 NIAH 族的 **Valhalla 适配版**：needle 埋在 filler 行中，经 `append_context` 写入 session 后提问 |
| **意味着什么** | **会话级长程召回** 在 62 行规模内可靠；与 RULER 互补（见 1.3） |
| **因为什么** | Needle 作为 corpus line 被 Fate/Space 索引；检索命中后 Hybrid 输出带 citation；**非** raw transformer 128K attention |
| **报告** | `needle_session_v1_test.json` |

### 1.3 RULER-style（合成 needle 族）

| 项 | 内容 |
|----|------|
| **测了几次** | **×1**（industry 全量跑分 2026-06-30） |
| **结果** | **20/20 (100%)** — single-needle + multi-needle · depth 5–40 |
| **对应什么** | RULER / U-NIAH 风格的 **可控 needle 检索**（bundle 内 synthetic，非官方 128K 全量） |
| **意味着什么** | 在 **更深、多 needle** 设定下 recall 仍满；比 Needle 4 点更宽覆盖 |
| **因为什么** | 同 session append + 结构检索；multi-needle 考验多条 corpus line 分别可检索 |
| **报告** | `ruler_v1_test.json` |

### 1.4 External holdout（套件外）

| 项 | 内容 |
|----|------|
| **测了几次** | **×1**（industry）+ 更早 internal runs 一致 |
| **结果** | **15/15 (100%)** — GSM8K 样例、MMLU 学科、地理/历史/中文等 |
| **对应什么** | **训练/调参未覆盖** 的 15 题 holdout；open QA + 小 corpus |
| **意味着什么** | 非 benchmark 过拟合；结构路由在多样题型上泛化 |
| **因为什么** | Targeted open retrieval + hybrid；题目未出现在 fair/industry bundle 中 |
| **报告** | `external_holdout_test.json` |

### 1.5 MCQ ladder（Qwen lm_patch 缩放）

| 项 | 内容 |
|----|------|
| **测了几次** | fast slice n=10：**×1**（0.5B 70% → 3B 100%）；**full fair MCQ n=46 ×1**（2026-06-30 加强下载后 industry run） |
| **结果** | **0.5B: 30/46 (65.2%)** → **3B: 45/46 (97.8%)** · slope **+0.419**/log₁₀(params) · R²=1.0 |
| **对应什么** | Fair suite **46 题 MCQ**（多领域）；同一 Valhalla patch 换 **Rust Candle sharded Qwen** backbone |
| **意味着什么** | **结构 + lm_patch 随参数量缩放**；3B 在该 MCQ 集接近饱和；证明 patch 加载链（`model.safetensors.index.json`）可用 |
| **因为什么** | lm_patch 在 Hybrid decode 中做 logprob MCQ；更大 backbone → 更强语言 prior；与 open retrieval **正交**（MCQ 测 patch，不测 RAG corpus） |
| **报告** | `mcq_ladder_v1_test.json` · `MCQ_LADDER_20260630.md` |

### 1.6 Valhalla 原生套件（非第三方，但有效）

| Benchmark | 次数 | 结果 | 对应什么 | 意味着 | 因为什么 |
|-----------|------|------|----------|--------|----------|
| Long memory | 多轮 | **73/76 (96.0%)** | append-then-ask 四 arm | 长久记忆生产协议 | E7 algebra corpus feedback |
| Proactive Fate v2 | ×1 | **72/72 · PPI 0.921** | 主动探针 + 门控 | 低幻觉 proactive | Exit/FIR/warmup 修复 |
| Open retrieval targeted | ×1 | **31/31 (100%)** | fair scaling open arm | 结构检索 backbone 无关 | Fate rerank 不依赖 LM 大小 |
| Follow-up native 30-turn | 历史 | **96.7%** | 多轮对话 | 上下文连贯 | session persistent |

---

## 2. Tier B — 有效数据，分数须带条件说明

### 2.1 LongBench-v2（THUDM）

| 项 | 内容 |
|----|------|
| **测了几次** | **×1** |
| **结果** | **7/20 (35%)** · `length=short` slice |
| **对应什么** | 官方 LongBench-v2 **短上下文 MCQ**；context 截断 **12k chars / ≤32 corpus lines** |
| **意味着什么** | 0.5B + 截断下 **诚实下界**；不可 claim 接近 human ~53.7% overall |
| **因为什么** | 长文被截断；0.5B lm_patch MCQ 能力有限；部分题为 multi-doc / long-dialogue 仍超 Valhalla session 设计 |
| **报告** | `longbench_v2_v1_test.json` |

### 2.2 MultiHop-RAG（COLM 2024）

| 项 | 内容 |
|----|------|
| **测了几次** | **×1** |
| **结果** | **9/25 (36%)** |
| **对应什么** | 新闻 **多跳** QA；evidence `fact` 行作 corpus（已过滤空 evidence） |
| **意味着什么** | 开放域多跳 **发展中**；高于随机、远低于 RAGTruth 式单跳忠实 |
| **因为什么** | 需跨多条 evidence 推理 + 短句 corpus；0.5B open 推理弱于 trad LM 长 prompt |
| **报告** | `multihop_rag_v1_test.json` |

### 2.3 LaRA-style（RAG vs Long-Context）

| 项 | 内容 |
|----|------|
| **测了几次** | **×1** |
| **结果** | Valhalla **RAG 5/20 (25%)** · trad LM **LC 14/20 (70%)** |
| **对应什么** | LaRA 论文设定：**短 RAG corpus** vs **padding 长 context**（MultiHop 衍生 20 题） |
| **意味着什么** | **重要负结果**：推理型新闻 QA 上，trad 长 prompt **显著优于** Valhalla 短结构 RAG |
| **因为什么** | LC arm 把 evidence 埋进 40+ filler 行长上下文，0.5B trad 仍可做链式推理；Valhalla RAG 仅 2–4 行 evidence，结构检索无法补全推理链 |
| **报告** | `lara_v1_test.json` |

### 2.4 LoCoMo（Snap ACL 2024）

| 项 | 内容 |
|----|------|
| **测了几次** | bundle 刷新后 **×1**（419 行/对话 full download）；此前 64-line cap **×1** 同 **1/30** |
| **结果** | **1/30 (3.3%)** |
| **对应什么** | 长对话记忆 QA；bundle 已有 **max 419 session lines**，但 runner 默认 **`--max-lines 64`** |
| **意味着什么** | 当前 **不能** 代表 LoCoMo 官方能力；分数反映 **协议 cap**，非 full dialogue |
| **因为什么** | `test_locomo_v1.py` 硬 cap 64 行；600-turn 对话需 **locomo-v2 chunked append**（roadmap）；非下载问题 |
| **报告** | `locomo_qa_slice30.json`（419 lines）· `locomo_v1_test.json` |

---

## 3. Tier C — 无效，勿引用分数

### 3.1 FRAMES（Google NAACL 2025）

| 项 | 内容 |
|----|------|
| **测了几次** | title-only corpus **×2**；wiki fetch **×1** 失败（Wikipedia 超时） |
| **结果** | **0/25 (0%)** |
| **为何无效** | FRAMES 定义依赖 **Wikipedia 正文** multi-hop RAG；当前 bundle `wiki_fetched=0`，corpus 仅为 `Reference: <url>` 占位 |
| ** paper baseline** | naive **40.8%** · oracle **72.9%**（有 wiki 时） |
| **下一步** | 在有 wiki 网络的环境生成 `cache/wiki/`，或拷贝缓存后 `--offline` 重建 bundle |
| **报告** | `frames_v1_test.json`（**标记 FRAMES_NEEDS_WIKI_CORPUS**） |

---

## 4. 总表（仅有效 A + 条件 B）

| # | Benchmark | 有效性 | 次数 | 结果 | 一句话 |
|---|-----------|--------|------|------|--------|
| 1 | RAGTruth 40Q | A | ×2 | 40/40 | RAG 忠实度 industry 强 |
| 2 | RAGTruth 100Q | A | ×1 | 100/100 | 含 hallucination label 仍全 grounded |
| 3 | Needle session | A | ×2 | 4/4 | 62 行内会话召回满 |
| 4 | RULER-style | A | ×1 | 20/20 | 深/多 needle 检索满 |
| 5 | External holdout | A | ×1 | 15/15 | 套件外泛化满 |
| 6 | MCQ ladder 46Q | A | ×1 full | 65%→98% | lm_patch 随参数量缩放 |
| 7 | Long memory | A | 多轮 | 96.0% | 原生长久记忆 |
| 8 | LongBench-v2 | B | ×1 | 35% | 0.5B+截断诚实边界 |
| 9 | MultiHop-RAG | B | ×1 | 36% | 多跳开放 QA 发展中 |
| 10 | LaRA RAG vs LC | B | ×1 | 25% vs 70% | 推理型 LC 占优（负结果） |
| 11 | LoCoMo | B† | ×1 | 3% | †64-line cap，非 full LoCoMo |
| 12 | FRAMES | C | — | 0% | **无效**，缺 wiki |

---

## 5. 对外一句话（仅用 Tier A）

> **RAGTruth 100/100 · Needle 4/4 · RULER 20/20 · Holdout 15/15 · MCQ 0.5B→3B 65%→98%** — ValhallaBase 在 RAG 忠实度、会话 needle 召回、套件外泛化与 backbone 缩放上有 industry 级证据；LongBench/MultiHop/LaRA 给出诚实边界；LoCoMo/FRAMES 待协议或 corpus 补齐后再报分。

---

## 6. 勿对外声称

- FRAMES **0%** 作为模型能力
- LoCoMo **3%** 作为 Snap 官方 benchmark 分数
- LongBench **35%** 接近 SOTA 或 human baseline
- MCQ ladder **10 题 fast slice** 与 **46 题 full** 混用（对外用 **46 题**）

---

## 7. 复现

```bash
# 加强下载 bundle
HF_ENDPOINT=https://hf-mirror.com .venv-llm/bin/python3 tools/standard_benchmarks/download_standard_benchmarks.py --all --no-wiki-fetch

# Industry 全量跑分
RUSTFLAGS="-L /opt/cuda/lib64" cargo build -p hub-f64 --release --bin valhalla_base
RUSTFLAGS="-L /opt/cuda/lib64" python3 tools/valhalla_inference/run_industry_benchmarks.py --all

# 仅有效 Tier A 子集
python3 tools/valhalla_inference/run_recognized_benchmarks.py
```

---

*Rogue Intelligence LNC. · 2026-06-30*
