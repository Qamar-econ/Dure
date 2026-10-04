---
title: Dure Reader
emoji: ☕
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
---
Dure AI message reader. A 0.5B open model (Qwen2.5-0.5B-Instruct, Apache-2.0) fine-tuned with LoRA
to read coffee farmers' SMS in Tetum and English and return language, crop, quantity, lowest price,
grade words and yes/no as JSON. Dure's rules engine reads most texts on its own; this model reads the ones it isn't sure about. `POST /parse {"msg": "...", "expect": "none|kg|ask|decide"}`.
