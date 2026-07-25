# 03 — Priority Inversion Problem

> This note explains the head-of-line blocking / priority inversion problem that InterruptLLM solves.

## The scenario

Imagine a GPU serving two tenants:

- **Tenant A:** Interactive chatbot. Users expect responses in < 200 ms.
- **Tenant B:** Document summarization. Responses in a few seconds are acceptable.

A long summarization request arrives first and starts decoding. A chat request arrives one second later.

Under FCFS continuous batching:

```mermaid
flowchart LR
    A[Summarization starts] --> B[Chat request arrives]
    B --> C[Chat waits]
    C --> D[Summarization finishes 10 s later]
    D --> E[Chat finally runs]
```

The chat user waits 10 seconds for a response that should take milliseconds.

## Priority inversion

**Priority inversion** happens when a low-priority task prevents a high-priority task from running.

In this case:

- The summarization request has low priority.
- The chat request has high priority.
- The low-priority request is already running, so the high-priority request waits.

> [!important]
> Priority inversion is not just a queueing delay. It is a structural problem caused by non-preemptive scheduling.

## Head-of-line blocking

**Head-of-line blocking** occurs when a long request at the front of the queue blocks all later requests.

In LLM serving, the "line" is the running batch. The long summarization job is at the head of the line.

```
Queue: [Long job] [Chat] [Chat] [Short job]
         ↑
    blocks everyone
```

## The P99 latency problem

The paper reports that this effect inflates interactive P99 latency by up to **17×**.

Why P99? Because even if most chat requests arrive when the GPU is idle, the unlucky 1% arrive during a long batch job and wait a very long time.

> [!important]
> Tail latency (P99) is what users actually experience as "slowness." Average latency can look fine while P99 is terrible.

## Why existing solutions are insufficient

| Approach | Why it fails |
|---|---|
| **Continuous batching** | Does not evict running requests. |
| **Priority queue** | Only reorders admission; cannot preempt. |
| **Speculative decoding** | Makes everyone faster but does not reorder priorities. |
| **Request migration** | Moving the full KV cache is too slow. |

## The ideal behavior

When a high-priority request arrives, the system should:

1. Pause the low-priority request at the next iteration boundary.
2. Save its state (KV cache + metadata).
3. Run the high-priority request immediately.
4. Later, restore the low-priority request and continue.

This is exactly what InterruptLLM does.

```mermaid
flowchart LR
    A[Summarization runs] --> B[Chat arrives]
    B --> C[Preempt summarization]
    C --> D[Run chat immediately]
    D --> E[Resume summarization]
```

## How this connects to InterruptLLM

The entire paper is motivated by this problem:

- Section II-B explains it with the 128K-token example.
- Figure 1 visualizes the FCFS vs. InterruptLLM timelines.
- Section VI shows that InterruptLLM reduces P0 P99 latency by 8.8× over FCFS.

> [!important]
> If you understand priority inversion and head-of-line blocking, you understand why the paper exists.

## Check your understanding

- [ ] I can explain priority inversion in one sentence.
- [ ] I can explain head-of-line blocking in LLM serving.
- [ ] I understand why P99 latency matters more than average latency.
- [ ] I can explain why continuous batching and priority queues are not enough.

## Exercises

1. Describe a real-world scenario (outside of LLMs) where priority inversion occurs.
2. Why does head-of-line blocking hurt P99 latency more than average latency?
3. A non-preemptive priority scheduler admits a high-priority request before a low-priority one. But the low-priority request arrived first and is already running. What happens?
4. Draw a timeline showing FCFS vs. InterruptLLM for a long batch job and a short chat request.

> [!warning]
> Do not underestimate how common this problem is. In real cloud LLM APIs, chat users and batch summarization users often share the same GPU cluster. Priority inversion is a daily production issue.
