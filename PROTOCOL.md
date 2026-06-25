# valhalla-unified-core-v1

## 原则

- **不隔离**：同一任务在同一 Triad session 内完成 text → tts → image 交错 pulse
- **无预设路由**：Hub / Tile / Stem 自由接收三模态
- **输出**：bake 为完整 Hugging Face causal LM（非 runtime patch）

## 与 universal-core 关系

| 布局 | 协议 | 用途 |
|------|------|------|
| 隔离 | `valhalla-universal-core-v1` | 验证跨模态共用核心（~0.85 patch 对齐） |
| **不隔离（本项目）** | **`valhalla-unified-core-v1`** | 生产 bake + 部署 |

Smoke 对比：不隔离 universal score **0.880** vs 隔离 **0.763**（+0.12）。

## Bake 流程

```
fair 语料 + TTS + SD-Turbo 生图
    → valhalla_trimodal_incubate（持久单 session 融合）
    → bake_valhalla_model
    → finalize_hf_repo
    → models/hf/Qwen2.5-0.5B-Unified-Core-v1-{phase}-s{strength}/
```
