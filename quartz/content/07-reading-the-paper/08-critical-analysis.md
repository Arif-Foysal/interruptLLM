# 08 — Critical Analysis

> This note teaches you to read the paper critically. It gives you a checklist of questions to ask about any systems paper, applied to InterruptLLM.

## Why critical analysis matters

Reading a paper is not the same as accepting it. A good researcher asks:

- What is the claim?
- What evidence supports it?
- What assumptions are hidden?
- What could go wrong?
- What would make the result stronger?

## The CLAIM framework

Use this framework to analyze any systems paper:

| Letter | Question |
|---|---|
| **C** | What is the **Claim**? |
| **L** | What is the **Limitation**? |
| **A** | What is the **Assumption**? |
| **I** | What is the **Ideal** follow-up? |
| **M** | What is the **Metric**? |

## Applied to InterruptLLM

### C: Claim

InterruptLLM reduces interactive P99 latency by 8.8× over FCFS and 2.1× over non-preemptive priority, with 2.2% throughput loss.

> Is this claim well-supported? Yes, by the simulator and the calibration benchmark.

### L: Limitation

The main limitation is that the evaluation is simulation-based. The 0.5 ms swap penalty is a parameter, not a measured end-to-end preemption latency.

> How serious is this? It depends on whether the simulator's assumptions are realistic. The P100 benchmark partially validates the key assumption.

### A: Assumption

Key assumptions include:

- The swap penalty is small (0.5 ms) because only a hot footprint is evicted.
- The Kaggle trace is representative of multi-tenant workloads.
- P0 requests are latency-sensitive and P1 requests are delay-tolerant.

> Do these assumptions hold in real deployments? Sometimes, but real workloads are more complex.

### I: Ideal follow-up

An ideal follow-up would:

- Implement the scheduler inside vLLM.
- Measure real end-to-end preemption latency.
- Test on multiple production traces.
- Evaluate multi-GPU deployments.

### M: Metric

The paper uses P99 latency, throughput, Jain fairness, and SLA violations. These are reasonable, but real systems might also care about:

- TTFT P99
- Cost per token
- Energy consumption
- Multi-tenancy isolation guarantees

## Critical questions for the paper

### About the problem

- Is head-of-line blocking the most important problem in LLM serving?
- Do production systems already handle this differently (e.g., dedicated GPU pools)?
- Are P0 and P1 classes clearly separable in practice?

### About the design

- Is MLFQ the best choice, or would an earliest-deadline scheduler work better if deadlines were known?
- Why is the largest-footprint victim policy best? What if future workloads differ?
- Is CPU DRAM always available and fast enough?

### About the evaluation

- Does the 0.5 ms penalty hold for real vLLM preemption with CUDA graphs?
- How would the system behave with very long-context (1M token) requests?
- Does the single-trace evaluation limit generalizability?

### About the baselines

- Are the baselines (FCFS, Priority, SSJF, etc.) representative of real systems?
- Would a better-tuned priority baseline close the gap?
- Is the comparison fair in terms of implementation effort?

## What the paper does well

- Clear problem statement.
- Honest limitations.
- Multiple baselines and ablations.
- Real GPU calibration benchmark.
- Confidence intervals via 20 runs.

## Where the paper could be stronger

- No real vLLM integration.
- Single trace.
- Single GPU generation measured.
- 0.5 ms penalty is not directly measured.
- No theoretical starvation proof.

## How to form your own opinion

After reading the paper, answer these three questions:

1. **Do I believe the problem is real?** Yes, priority inversion in shared GPU clusters is real.
2. **Do I believe the solution would work?** Probably, but a real prototype is needed.
3. **Is the evaluation convincing enough?** For a workshop, yes. For a top-tier conference, a real implementation would help.

## Check your understanding

- [ ] I can use the CLAIM framework to analyze a paper.
- [ ] I can list the main strengths of the paper.
- [ ] I can list the main weaknesses of the paper.
- [ ] I can form my own opinion about whether the results are convincing.

## Exercises

1. Apply the CLAIM framework to a different paper you have read.
2. Write a one-paragraph critique of InterruptLLM from the perspective of a skeptical reviewer.
3. If you had one extra month, what experiment would you add to make the paper stronger?
4. What is the most important assumption that, if wrong, would invalidate the main result?

> [!important]
> Critical analysis does not mean being negative. It means being precise about what is proven, what is assumed, and what remains open.

> [!question]
> Final reflection: If you were a reviewer, would you accept this paper? Why or why not?
