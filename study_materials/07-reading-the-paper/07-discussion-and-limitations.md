# 07 — Discussion and Limitations

> This note guides you through Section VII of the paper: limitations, threats to validity, and future work.

## Section VII structure

| Part | Content |
|---|---|
| Limitations | Simulator abstractions, single trace, single GPU generation |
| Threats to validity | Internal, external, construct |
| Practical integration | What a real vLLM integration would require |

## Limitations

The paper is explicit about what the evaluation does not show:

1. **Simulator abstraction:** The GPU is modeled as a token-generation rate. Kernel launch, CUDA graph, and allocator overhead are omitted.

2. **0.5 ms penalty is a parameter:** It reflects a small hot footprint (2.5 MB at 5 GB/s), not a full KV-cache swap.

3. **Single trace:** Results are based on one Kaggle inference trace.

4. **Single GPU generation:** P100 measurements are PCIe Gen3; newer GPUs would reduce latency.

5. **Not a vLLM integration:** The prototype is a simulator, not a production engine patch.

> [!important]
> A strong systems paper acknowledges limitations honestly. The paper does not oversell the results.

## Threats to validity

### Internal validity

Internal validity asks: are the results caused by the scheduler, not something else?

Threats:

- The 0.5 ms swap penalty is a parameter, not a measured end-to-end preemption latency.
- The GPU benchmark only validates the raw memcpy component.
- Mitigations: fixed seeds, 20 runs, ±10% arrival jitter.

### External validity

External validity asks: do the results generalize to other settings?

Threats:

- The Kaggle trace may not capture all production behaviors (multi-modal, speculative decoding, prefix caching).
- P100 is older hardware; newer GPUs would shift absolute latencies.

> [!important]
> The paper argues that relative policy ordering is robust across loads and swap penalties, so the conclusions likely generalize even if absolute numbers change.

### Construct validity

Construct validity asks: are we measuring the right things?

Threats:

- SLA satisfaction is approximated by P99 latency and Jain indices.
- Real systems may use TTFT percentiles, cost budgets, or other metrics.

## Practical integration

The paper explains what a real vLLM integration would require:

- Handling CUDA graphs
- Handling PyTorch allocator interactions
- Using DMA streams for GPU→host transfers
- Managing the P1/P0 trade-off intentionally

The P1/P0 P99 ratio of 19× at ρ=0.93 is a design choice: interactive users need fast responses, batch users tolerate delays.

## Future work

The paper lists future directions:

- Extend to multi-GPU tensor-parallel deployments
- Add formal starvation-freedom proofs
- Collect real GPU preemption latency measurements
- Integrate with vLLM or another production engine

## Connections to background modules

| Concept | Module |
|---|---|
| Simulator abstraction | [[03-simulation-and-ablation]] |
| Threats to validity | [[03-simulation-and-ablation]] |
| CUDA graphs/allocator | [[02-cuda-and-bandwidth]] |
| Swap measurements | [[03-measuring-swap-latency]] |

## Check your understanding

- [ ] I can list the main limitations of the paper.
- [ ] I can explain internal, external, and construct validity threats.
- [ ] I understand what a real vLLM integration would require.
- [ ] I can summarize the future work directions.

## Exercises

1. What is the most important limitation for a production deployment? Why?
2. Give an example of an external validity threat not mentioned in the paper.
3. How does the paper argue that the relative conclusions are robust despite hardware differences?
4. Why is the P1/P0 ratio of 19× a design choice rather than a failure?

> [!tip]
> When reading a research paper, the limitations section is often where you find the best ideas for future work. The author is telling you exactly what is not yet done.
