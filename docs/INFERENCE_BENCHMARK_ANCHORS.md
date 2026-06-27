# Inference Benchmark Anchors

Explicit one-line facts for local-corpus-demo and holdout eval. Ingested by `run_local_corpus_demo.py`.

- Open questions in hybrid routing use **native** structure retrieval by default (not lm_patch).
- Hybrid decode routes MCQ questions to **lm_patch** with LM **logprob** by default; open questions use **native** structure retrieval.
- The valhalla_base binary uses **JSON** on **stdin** and **stdout** for requests and responses.
- **Triad** incubation runs Hub, Tile, and StemCell in parallel before Fate snapshot export.
- Production default fate ingress routing is **quad_cycle** (four-system quad routing).
- ValhallaBase session teach does **not** perform gradient **weight updates** on LM weights (zero-weight ingest only).
- Proactive idle spread gate uses **tau(0)=12/138** scaled by E7 parameters (δ/(dim+r)); minimum **hub_prefs_spread** applies before self-probe.
- The context flexibility maximum goal document is **CONTEXT_FLEXIBILITY_MAX_GOAL.md** in valhalla-unified-core docs.
- **FOG** abbreviates **Fate Output Gate** — Fate decides when to emit, abstain, or defer.
- Fair holdout evaluation uses the **open_retrieval** slice from fair-1.2 benchmark (corpus-grounded open QA).
- Unified inference experiment records live in **valhalla-unified-core** under docs/EXPERIMENT_RECORD_INFERENCE_PARADIGM.md.
- Default runtime patch body for LM decode head is **triad** (Hub + Tile + StemCell bundle).
- Recommended production follow-up decode mode is **native_follow_up_aware** for multi-turn dialogue.
