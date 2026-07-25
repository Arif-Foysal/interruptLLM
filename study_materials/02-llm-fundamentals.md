# Module 02 — LLM Fundamentals

> This module explains what Large Language Models are, how the transformer works, how autoregressive generation works, and what the KV cache is.

## Why this module matters

You cannot understand InterruptLLM without understanding what LLM inference actually does. This module builds the conceptual model: token-by-token generation, prefill vs. decode, and the KV cache as the memory bottleneck.

## Notes in this module

1. [[01-what-are-llms]] — Language models, tokens, autoregression, inference vs. training
2. [[02-transformer-and-attention]] — Transformer architecture, self-attention, Q/K/V, KV cache intuition
3. [[03-autoregressive-generation]] — Prefill vs. decode, TTFT, TPOT, iteration boundaries
4. [[04-kv-cache-explained]] — What the KV cache stores, how big it gets, 16 bytes/token checkpoint metadata

## Key takeaways

- LLMs generate one token at a time.
- Prefill processes the prompt; decode generates output.
- The KV cache stores K and V vectors for all previous tokens.
- KV cache size grows with sequence length and is the main memory bottleneck.

## Check your understanding

- [ ] I can explain autoregressive generation.
- [ ] I know the difference between prefill and decode.
- [ ] I can estimate KV cache size for a given sequence length.
- [ ] I understand why the KV cache makes preemption expensive.

## Time estimate

- 4–6 hours for a beginner
- 2 hours if you already know transformers

## Connections to the paper

These concepts directly support:

- Section II-A: LLM Inference and Continuous Batching
- Section II-B: PagedAttention
- Section IV-D: State Checkpoint Engine

## Previous / next

- Previous: [[01-prerequisites]]
- Next: [[03-gpu-and-memory]]

> [!important]
> The KV cache is the central object of the paper. Spend extra time on [[04-kv-cache-explained]] if needed.
