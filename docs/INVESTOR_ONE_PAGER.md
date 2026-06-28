# Valhalla Unified Core — Investor One-Pager

**Rogue Intelligence LNC. · ValhallaBase · 2026-06-27 · Confidential**

---

## One sentence

**Valhalla matches compact LM RAG on accuracy (96.8%) while offering pollution-safe session routing, algebraic output governance, flat context transport, and auditable hybrid routing that black-box LLMs cannot replicate without protocol changes.**

---

## Four structural differentiators

### D4 — Session routing rescues polluted memory (+61pp)

Dumping an entire domain corpus into a session and batch-evaluating destroys accuracy: **35.5%**. Valhalla's production protocol—clear corpus, per-question targeted ingest, fresh transfer eval—restores **96.8%**, a **+61.3pp** lift [+45.2, +77.4] (paired n=31).

**Why it matters:** Enterprise knowledge bases grow daily. RAG-with-memory products that treat "bigger session = better" fail silently. Valhalla makes routing a first-class, auditable discipline.

---

### D7 — FOG: Fate decides *when* to speak (96.6% precision)

The **Fate Output Gate** uses E7-integer thresholds (τ = 12/138, no fitted floats) to emit, abstain, or defer. Emitted answers are **96.6%** precise [82.8%, 99.4%]; distractor corpora trigger abstain rather than confident hallucination.

**Why it matters:** Regulated buyers need systems that can *refuse*—not just generate. FOG is compliance-grade output governance, not a post-hoc confidence score.

---

### D8 — Proactive without unsolicited hallucination (UP 100%)

On idle, Fate self-probes topic continuity, passes FOG, and may nudge with grounded corpus text. **100%** of emitted nudges stay on-topic [87.5%, 100%]; mismatch corpora abstain **88.2%** of the time with **0%** false interrupt rate.

**Why it matters:** Proactive assistants usually hallucinate or interrupt. Valhalla couples initiative with the same algebraic gate that blocks low-evidence output.

---

### D5 — Context transport: ~64 chars/step vs full prompt resend

Internal context grows linearly with session appends; wire payload averages **~64 chars per step** vs **752-char** full-prompt resends (**3.62×** growth on 12-step curve). Token-efficiency-v1: LM prefill on native path stays **question-only**; RAG resends full corpus each turn.

**Why it matters:** Multi-turn vertical AI on edge hardware pays for every token. Structure-first memory changes *how* context is carried—not just benchmark accuracy.

---

## Headline numbers (Wilson 95% CI)

| Metric | Result |
|--------|--------|
| Fair holdout RAG | **96.8%** [83.8%, 99.4%] |
| vs Qwen2.5-0.5B RAG | **+0.0pp** [-9.7, +9.7] (statistical tie) |
| Transfer vs polluted | **+61.3pp** [+45.2, +77.4] |
| FOG emit precision | **96.6%** [82.8%, 99.4%] |
| Proactive UP \| emit | **100%** [87.5%, 100%] |
| Crosslang / external / local | **100%** on latest batteries |
| **MCQ hybrid lm_patch** | **65.2%** [50.8%, 77.3%] |
| MCQ vs trad_lm | **+37pp** [+21.7, +52.2] |
| Token prefill vs RAG | **0.29×** @ 96.8% holdout |
| NPPI paradigm index | **0.884** [0.848, 0.984] |

---

## Honest boundaries (pre-registered)

- Not a weight fine-tune replacement on holdout (`SESSION_SNAPSHOT_NO_HOLDOUT_LIFT_BEYOND_RAG`)
- Raw open_retrieval ceiling ties traditional LM RAG; value is routing, governance, transport, multimodal core
- Companion model deliberately small (Qwen2.5-0.5B) to prove structure layer value

---

## Product stack

```
ValhallaBase(decode="hybrid", follow_up_decode="native_follow_up_aware",
             fate_ingress_routing="quad_cycle", fate_qa_feedback=True)
```

JSON stdin/stdout · on-prem · per-answer routing audit trail

---

## Assets

| Doc | Path |
|-----|------|
| Full distinctive capabilities | `docs/DISTINCTIVE_CAPABILITIES_CN.md` |
| TeX paper | `papers/ValhallaBase_Distinctive_Inference_Paradigm.pdf` |
| Confidence report | `reports/valhalla_inference/CONFIDENCE_REPORT_v1.md` |
| Experiment record | `docs/EXPERIMENT_RECORD_INFERENCE_PARADIGM.md` |

**Contact:** Rogue Intelligence LNC. · Valhalla Unified Core
