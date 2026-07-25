# Module 05 — LLM Serving Systems

> This module bridges OS concepts to real LLM serving systems. It covers PagedAttention, continuous batching, and the priority inversion problem.

## Why this module matters

This module answers the question: "Why can't existing systems like vLLM already do this?" It explains the specific constraints that make LLM serving non-preemptive and why PagedAttention changes the game.

## Notes in this module

1. [[01-vllm-and-pagedattention]] — vLLM's block tables and why blocks are swappable
2. [[02-continuous-batching]] — How continuous batching works and why it is non-preemptive
3. [[03-priority-inversion-problem]] — Head-of-line blocking, priority inversion, P99 impact

## Key takeaways

- PagedAttention stores KV cache in swappable blocks.
- Continuous batching is cooperative: requests run to completion.
- A long batch job can block short interactive requests for seconds.
- This inflates P99 latency dramatically.

## Check your understanding

- [ ] I can explain PagedAttention's block table.
- [ ] I understand why continuous batching is non-preemptive.
- [ ] I can explain head-of-line blocking and priority inversion.
- [ ] I know why P99 latency is the right metric.

## Time estimate

- 3–4 hours for a beginner
- 1.5 hours if you already know vLLM

## Connections to the paper

These concepts directly support:

- Section I: Introduction (problem statement)
- Section II: Background and Motivation
- Section III: Related Work

## Previous / next

- Previous: [[04-operating-systems-concepts]]
- Next: [[06-evaluation-methodology]]

> [!important]
> This module explains the problem. The next module explains how the paper measures the solution.
