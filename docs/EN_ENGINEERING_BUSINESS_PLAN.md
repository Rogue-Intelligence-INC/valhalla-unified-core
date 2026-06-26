# Valhalla Unified Core — Engineering Business Plan

**Document type:** Business plan (engineering-led)  
**Product:** Valhalla Unified Core (VUC)  
**Version:** vuc-bp-1.0 · **Date:** 2026-06-26  
**Publisher:** Rogue Intelligence LNC.  
**Audience:** Investors, strategic partners, enterprise buyers  
**Companion docs:** [Whitepaper](./EN_ENGINEERING_WHITEPAPER.md) · [Due Diligence](./EN_ENGINEERING_DUE_DILIGENCE.md)

---

## 1. Executive summary

Enterprises need AI that **uses their documents and multimodal assets** without hallucinating off-corpus facts or bleeding topics across sessions. Transformer-only stacks optimize token generation; they do not natively provide **auditable corpus binding**, **incremental context**, or **same-task multimodal alignment**.

**Valhalla Unified Core (VUC)** is a proprietary inference platform that:

1. Incubates customer corpus + multimodal context into a **Triad structure snapshot** (not prompt stuffing).
2. Fuses text, TTS, and image in **one session** (non-isolated universal core → ~1.0 shared patch).
3. Answers open questions with **`[corpus:k]` grounded retrieval** — **97%** on fair open_retrieval (31 tasks), **0%** cross-topic hallucination in controlled drift protocols.
4. Ships a **small LM as decode head** for MCQ/numeric (**63%** @ 46 MCQ) while keeping structure path for zero-generate deployments.

**Differentiators (evidence-backed):**

| Highlight | Engineering proof |
|-----------|-------------------|
| **Zero cross-topic hallucination** | 0/48 drift probes (swap + interleave + 30-turn extended) |
| **Context fidelity** | 100% context-swap fidelity (12/12) |
| **Multimodal fusion** | 107/107 non-isolated universal core wins |
| **Session context** | ~64 chars/step append vs full prompt regrowth |
| **Production-ready stack** | Documented defaults + JSON reproducibility |

---

## 2. Problem & market

### 2.1 Problem

| Pain | Incumbent behavior | VUC behavior |
|------|-------------------|--------------|
| RAG hallucination | Model paraphrases or invents | Native retrieval + distractor 0% false confidence |
| Topic drift in long chats | Attention dilution / wrong recall | 96.7% on-topic @ 30 turns; follow-up-aware retrieval |
| Multimodal inconsistency | Late fusion in LM layers | Non-isolated core fusion in structure layer |
| Audit / compliance | Opaque generation | `[corpus:k]` line citations |
| Cost of context | Resend full history each turn | Session append fingerprint |

### 2.2 Target customers

| Segment | Use case | VUC fit |
|---------|----------|---------|
| Regulated QA | Policy, clinical, legal corpus Q&A | Grounded retrieval + drift tests |
| Industrial / IoT | Manuals + sensor/text/audio logs | Multimodal core fusion |
| Ed-tech / assessment | MCQ + open explanation | Hybrid decode |
| On-prem AI | Air-gapped corpus, small LM | Native path + optional bake |

### 2.3 Market positioning

**Not** a general foundation-model replacement. **Is** a **memory-and-context platform** with optional 0.5B–3B decode head — complementary to customer or hosted LLMs.

---

## 3. Product

### 3.1 ValhallaBase (primary SKU)

- API: JSON stdin/stdout · Python `ValhallaBase` wrapper
- Features: hybrid routing, session append, multimodal `context_items`, core fusion, Fate QA feedback
- Protocol: `valhalla-base-v1`

### 3.2 Baked HF product (deployment SKU)

- Bake non-isolated structure into Qwen-class weights
- Load via `ValhallaLLM` (transformers / vLLM) or `valhalla_fused_lm`
- Protocol: `valhalla-unified-core-v1`

### 3.3 Packaging

| Tier | Deliverable |
|------|-------------|
| **Evaluate** | Benchmark scripts + sample reports (this repo) |
| **Deploy** | Licensed binaries + bake pipeline + support |
| **Enterprise** | Custom corpus onboarding, SLA, private bake |

---

## 4. Go-to-market

### Phase 1 — Technical proof (current)

- Publish engineering whitepaper + DD pack (this repo)
- Fair-benchmark reproducibility for prospects
- Pilot: customer corpus → ValhallaBase API → drift + retrieval metrics

### Phase 2 — Bake & serve

- Customer-specific HF bake @ s=0.08–0.10
- vLLM-compatible serving for MCQ/logprob workloads
- ValhallaBase orchestration for context-flex workloads

### Phase 3 — Platform

- Hosted context session service
- Multimodal ingress (TTS/image pipelines)
- QA→Fate continuous learning per tenant

---

## 5. Business model

| Stream | Model |
|--------|-------|
| License | Annual enterprise license (per deployment / seat) |
| Bake | Per-model export fee (corpus size tiers) |
| Support | Integration + benchmark attestation |
| Cloud | Managed ValhallaBase API (future) |

---

## 6. Competitive moat

1. **Reproducible structure metrics** — universal core, not marketing adjectives  
2. **Protocol-versioned benchmarks** — `context-topic-drift-v2`, fair-1.2  
3. **Hybrid architecture** — one product, native + LM paths  
4. **Proprietary Triad body** — Hub/Tile/Stem/Fate; bake into weights  
5. **Non-isolated fusion IP** — single-session multimodal layout  

---

## 7. Metrics dashboard (June 2026)

| KPI | Value | Source |
|-----|-------|--------|
| Open retrieval accuracy | **97%** | `scale_benchmark_test.json` |
| Context swap fidelity | **100%** | `context_topic_drift_test.json` |
| Cross-topic hallucination (drift suite) | **0%** | drift reports |
| 30-turn on-topic | **96.7%** | `context_topic_drift_extended_test.json` |
| Non-isolated core win rate | **100%** (107/107) | `scale_benchmark_test.json` |
| Core fusion QA lift (12 tasks) | **+8.3 pp** | `context_core_fusion.json` |
| MCQ (LM) | **63%** | `scale_benchmark_test.json` |

---

## 8. Roadmap (12 months)

| Quarter | Milestone |
|---------|-----------|
| Q3 2026 | vLLM bake validation; enterprise pilot template |
| Q4 2026 | Real-modality bake @ 107 scale; MCQ logprob compose v2 |
| Q1 2027 | Managed session API; tenant Fate feedback |
| Q2 2027 | 3B decode head; retrieval↔Fate coupling |

---

## 9. Team & legal

**Rogue Intelligence LNC.** — Proprietary technology.  
**NOT OPEN SOURCE.** Evaluation under NDA; commercial terms via **licensing@rogue-intelligence.com**

---

## 10. Investment ask (template)

Use with financial model separately. Engineering readiness:

- ✅ Production config documented  
- ✅ Drift / hallucination test suite  
- ✅ Multimodal fusion at scale  
- ⚠️ MCQ headroom (63% → target 75% via logprob compose)  
- ⚠️ Baked-loader context parity tests (planned)  
