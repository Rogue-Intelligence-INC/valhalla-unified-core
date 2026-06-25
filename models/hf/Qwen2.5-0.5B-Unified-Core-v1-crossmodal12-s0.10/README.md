---
license: apache-2.0
base_model: Qwen/Qwen2.5-0.5B-Instruct
tags:
  - valhalla
  - text-generation
  - qwen2
  - multimodal-fusion
library_name: transformers
pipeline_tag: text-generation

---

# Qwen2.5-0.5B-Unified-Core-v1-crossmodal12-s0.10

Valhalla-baked causal LM derived from [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct).

| Field | Value |
|-------|-------|
| Product | `valhalla-unified-core-v1` |
| Bake mode | `full` |
| Strength | `0.1` |
| Body | `triad` |
| Baked at | `2026-06-25T18:40:17.654846+00:00` |
| Weight delta norm | `298.1954322164847` |

Structure incubation: tiles=63, stem=181, signals=405504.



## Load (standard Hugging Face)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "/home/jouly/AI/Valhalla/valhalla-unified-core/models/hf/Qwen2.5-0.5B-Unified-Core-v1-crossmodal12-s0.10"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
```

## Valhalla fused LM (optional, same weights)

```bash
valhalla_fused_lm --model /home/jouly/AI/Valhalla/valhalla-unified-core/models/hf/Qwen2.5-0.5B-Unified-Core-v1-crossmodal12-s0.10 --phase test
```

`valhalla_manifest.json` documents incubation metadata; `transformers` ignores it at load time.

---
*Rogue Intelligence LNC. — Valhalla free multimodal fusion bake*
