# Glossary

> Key terms used throughout the curriculum and the paper, in alphabetical order.

## A

**Ablation study**
An experiment that removes or disables one component to measure its contribution. The paper's ablation (Table IV) shows that preemption is the dominant source of latency improvement.

**Admission Controller**
The InterruptLLM component that accepts or rejects requests based on predicted resource needs and current load. See [[03-system-design-deep-dive]].

**Aging**
A mechanism that promotes long-waiting requests to a higher priority class to prevent starvation. See [[03-mlfq-deep-dive]].

**Autoregressive generation**
Generating text one token at a time, feeding each generated token back into the model to produce the next. See [[03-autoregressive-generation]].

## B

**Batch capacity**
The maximum number of requests that can run in one decode iteration. The paper uses 16.

**Block**
In PagedAttention, a fixed-size chunk of KV cache (default 16 tokens). See [[01-vllm-and-pagedattention]].

**Block table**
A per-request mapping from logical block indices to physical GPU memory locations. See [[01-vllm-and-pagedattention]] and [[04-virtual-memory-and-paging]].

## C

**Checkpoint Engine**
The InterruptLLM component that saves request metadata (block table, position IDs, sampling state) so a preempted request can resume. See [[03-system-design-deep-dive]].

**Confidence interval**
A range that likely contains the true value. The paper reports `mean ± std` from 20 runs. See [[02-confidence-intervals]].

**Context switching**
Saving the state of a running task and restoring another. In InterruptLLM, this means swapping the KV cache and metadata. See [[01-scheduling-fundamentals]].

**Continuous batching**
A serving technique that adds and removes requests at decode iteration boundaries to keep GPU utilization high. See [[02-continuous-batching]].

**Context Swapper**
The InterruptLLM component that moves KV blocks between GPU HBM, CPU DRAM, and NVMe SSD. See [[03-system-design-deep-dive]].

**CUDA**
NVIDIA's parallel computing platform for GPUs. See [[02-cuda-and-bandwidth]].

## D

**Decode phase**
The phase of LLM inference where tokens are generated one at a time. See [[03-autoregressive-generation]].

**Device**
In CUDA terminology, the GPU.

**Device-to-host (D2H) transfer**
Moving data from GPU memory to CPU memory. This is the core operation of InterruptLLM's swapper. See [[02-cuda-and-bandwidth]].

**Discrete-event simulation (DES)**
A simulation that jumps between events rather than modeling continuous time. See [[03-simulation-and-ablation]].

## E

**Earliest-Deadline-First (EDF)**
A scheduling policy that runs the request with the soonest deadline. See [[02-scheduling-algorithms]].

**Effective bandwidth**
Real measured data transfer rate, as opposed to ideal theoretical bandwidth. See [[03-measuring-swap-latency]].

## F

**Fairness**
How equally resources are distributed. The paper uses Jain indices. See [[01-performance-metrics]].

**First-Come, First-Served (FCFS)**
A non-preemptive scheduler that serves requests in arrival order. The main baseline in the paper. See [[02-scheduling-algorithms]].

## G

**GPU (Graphics Processing Unit)**
A massively parallel processor used for matrix multiplication and neural network inference. See [[01-computer-systems-basics]].

## H

**Head-of-line blocking**
When a long request at the front of a queue blocks all later requests. The main problem the paper addresses. See [[03-priority-inversion-problem]].

**High Bandwidth Memory (HBM)**
Fast memory on the GPU die. See [[01-gpu-memory-hierarchy]].

**Host**
In CUDA terminology, the CPU and its memory.

## I

**Iteration boundary**
The point between decode steps where the scheduler can add, remove, or preempt requests. See [[02-continuous-batching]].

## J

**Jain fairness index**
A metric ranging from 0 to 1 that measures equality of resource distribution. 1 means perfectly equal. See [[01-performance-metrics]].

## K

**KV cache**
The stored Key and Value vectors from previous tokens, used to speed up autoregressive generation. See [[04-kv-cache-explained]].

## L

**Latency**
The time from request arrival to completion. See [[01-performance-metrics]].

**Load factor (ρ)**
The ratio of offered load to GPU capacity. See [[01-performance-metrics]].

**Lottery scheduling**
A probabilistic scheduling policy that gives each request tickets and holds a random draw. See [[02-scheduling-algorithms]].

**LZ4**
A fast compression algorithm. The paper uses it to reduce swap size. See [[03-measuring-swap-latency]].

## M

**MLFQ (Multi-Level Feedback Queue)**
A scheduling algorithm with multiple priority queues and aging. Used by InterruptLLM. See [[03-mlfq-deep-dive]].

## N

**NVMe SSD**
A fast persistent storage device. Used as the third tier in InterruptLLM's memory hierarchy. See [[01-gpu-memory-hierarchy]].

## O

**Overhead**
Extra time or resources consumed by the scheduling mechanism itself. The paper reports 0.07 ms average preemption overhead.

## P

**P0 / P1 / P2 / P3**
InterruptLLM's four priority classes. P0 is highest priority (interactive), P3 is lowest (background). See [[03-mlfq-deep-dive]].

**Page fault**
In OS virtual memory, an access to a page not currently in physical memory. Analogous to a missing KV block in the GPU. See [[04-virtual-memory-and-paging]].

**Page table**
An OS data structure mapping virtual pages to physical frames. Analogous to vLLM's block table. See [[04-virtual-memory-and-paging]].

**PagedAttention**
vLLM's technique for storing KV cache in non-contiguous blocks. See [[01-vllm-and-pagedattention]].

**Paging**
Dividing memory into fixed-size pages for non-contiguous allocation and swapping. See [[04-virtual-memory-and-paging]].

**Percentile**
A value below which a given percentage of observations fall. P99 means 99% are below. See [[03-math-foundations]].

**Pinned memory**
CPU memory locked in place so the GPU can DMA directly to/from it. See [[02-cuda-and-bandwidth]].

**Preemption**
Interrupting a running task to run a more urgent one. The central idea of the paper. See [[01-scheduling-fundamentals]].

**Prefill phase**
The phase of LLM inference that processes the prompt and builds the initial KV cache. See [[03-autoregressive-generation]].

**Priority inversion**
When a low-priority task blocks a high-priority task. See [[03-priority-inversion-problem]].

## Q

**Quality of Service (QoS)**
Meeting latency or throughput targets for different classes of traffic.

## R

**Round-robin**
Serving requests in a class in cyclic order to prevent starvation within the class. See [[03-mlfq-deep-dive]].

## S

**Scheduling quantum**
The time interval between scheduler decisions. The paper uses 100 ms. See [[05-evaluation-walkthrough]].

**Seed**
A starting value for a random number generator that makes experiments reproducible. See [[02-python-for-research]].

**Self-attention**
A transformer mechanism where each token attends to all others. See [[02-transformer-and-attention]].

**Shortest-Remaining-Time-First (SRJF/SSJF)**
A scheduling policy that runs the request with the least remaining work. See [[02-scheduling-algorithms]].

**SLA (Service Level Agreement)**
A target performance level. The paper uses P99 < 200 ms for P0 and < 1 s for P1. See [[01-performance-metrics]].

**SLA violation rate**
The fraction of requests exceeding their SLA target. See [[01-performance-metrics]].

**Speculative decoding**
A technique to generate multiple tokens per decode step. It speeds up all requests but does not reorder priorities. Mentioned in [[03-priority-inversion-problem]].

**Standard deviation**
A measure of how spread out values are. The paper reports `mean ± std`. See [[03-math-foundations]].

**Swap penalty**
The time cost added to a preemption for moving KV blocks. The paper uses 0.5 ms. See [[03-measuring-swap-latency]].

## T

**Tail latency**
Latency at high percentiles (e.g., P99), which reflects worst-case user experience. See [[01-performance-metrics]].

**Throughput**
Number of tokens or requests completed per unit time. See [[01-performance-metrics]].

**Time-to-First-Token (TTFT)**
Time until the first generated token appears. See [[03-autoregressive-generation]].

**Time-Per-Output-Token (TPOT)**
Average time between generated tokens. See [[03-autoregressive-generation]].

**Token**
A small unit of text that LLMs process. See [[01-what-are-llms]].

## V

**vLLM**
An open-source LLM serving system that uses PagedAttention. See [[01-vllm-and-pagedattention]].

**Victim selection**
Choosing which request to preempt when space is needed. See [[03-mlfq-deep-dive]].

**Virtual memory**
A memory management technique that gives each process a contiguous address space mapped to non-contiguous physical frames. See [[04-virtual-memory-and-paging]].

## W

**Weighted Fair Queueing (WFQ)**
A scheduling policy that gives each class a share proportional to its weight. See [[02-scheduling-algorithms]].

## How to use this glossary

- Use `Ctrl+F` (or Obsidian search) to find terms quickly.
- If a term links to another note, read that note for a full explanation.
- Add your own terms as you encounter them.

> [!tip]
> Create your own flashcards from this glossary. The best way to remember terminology is active recall.
