# References and Further Reading

> A curated list of papers, videos, and articles for each topic covered in the curriculum.

## The InterruptLLM paper

- Nayem, Md Arif Faysal. **"InterruptLLM: A Preemptive Scheduling Framework for Low-Latency Multi-Tenant LLM Inference."** See `paper/main.tex` in this repository.
- GitHub repository: `https://github.com/mdzero591/ICCIT`
- Kaggle dataset: `bektursyn/llm-inference-logs-and-performance-metrics`

## LLM fundamentals

### Must-read papers

- Vaswani et al. **"Attention Is All You Need."** NeurIPS 2017. [[arxiv](https://arxiv.org/abs/1706.03762)] — The original transformer paper.
- Ouyang et al. **"Training Language Models to Follow Instructions with Human Feedback."** NeurIPS 2022. [[arxiv](https://arxiv.org/abs/2203.02155)] — InstructGPT / RLHF.

### Accessible explanations

- Jay Alammar, **"The Illustrated Transformer."** [[blog](https://jalammar.github.io/illustrated-transformer/)] — Highly visual explanation.
- Andrej Karpathy, **"Let's build GPT: from scratch, in code, spelled out."** [[YouTube](https://www.youtube.com/watch?v=kCc8FmEb1nY)] — Build a small GPT in PyTorch.
- Andrej Karpathy, **"Intro to Large Language Models."** [[YouTube](https://www.youtube.com/watch?v=zjkBMFhNj_g)] — High-level overview.

## LLM serving and vLLM

- Kwon et al. **"Efficient Memory Management for Large Language Model Serving with PagedAttention."** SOSP 2023. [[arxiv](https://arxiv.org/abs/2309.06180)] — The vLLM paper.
- Yu et al. **"Orca: A Distributed Serving System for Transformer-Based Generative Models."** OSDI 2022. [[paper](https://www.usenix.org/conference/osdi22/presentation/yu)] — Iteration-level scheduling.
- vLLM documentation: [[docs](https://docs.vllm.ai/)]

## GPU and CUDA

- NVIDIA CUDA documentation: [[docs](https://docs.nvidia.com/cuda/)]
- CUDA programming model overview: [[NVIDIA blog](https://developer.nvidia.com/blog/even-easier-introduction-cuda/)]

## Operating systems and scheduling

- OSTEP (Operating Systems: Three Easy Pieces)
  - Chapter on scheduling: [[link](http://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)]
  - Chapter on virtual memory: [[link](http://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf)]
- Arpaci-Dusseau and Arpaci-Dusseau, **Operating Systems: Three Easy Pieces.** Free textbook.

## Related systems papers

- Agrawal et al. **"Sarathi: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills."** ATC 2024. [[arxiv](https://arxiv.org/abs/2308.16369)]
- Zhong et al. **"DistServe: Disaggregating Prefill and Decoding for Goodput-Optimized LLM Serving."** arXiv 2024. [[arxiv](https://arxiv.org/abs/2401.09670)]
- Qin et al. **"Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving."** arXiv 2024. [[arxiv](https://arxiv.org/abs/2407.14279)]
- Sun et al. **"Llumnix: Dynamic Scheduling for Serverless LLM Serving."** ATC 2024. [[paper](https://www.usenix.org/conference/atc24/presentation/sun-biao)]
- Qiao et al. **"ConServe: Fine-grained GPU Harvesting for LLM Online and Offline Co-Serving."** arXiv 2024. [[arxiv](https://arxiv.org/abs/2410.01228)]
- Chen et al. **"TokenFlow: Responsive LLM Text Streaming Serving Under Request Burst via Preemptive Scheduling."** arXiv 2025. [[arxiv](https://arxiv.org/abs/2510.02758)] — Most closely related concurrent work.

## Math and statistics

- Khan Academy: Statistics and Probability [[link](https://www.khanacademy.org/math/statistics-probability)]
- 3Blue1Brown: "The Essence of Calculus" and "Linear Algebra" [[YouTube](https://www.youtube.com/c/3blue1brown)] — Visual intuition.

## Academic writing

- Patience et al. **"Ten Simple Rules for Writing and Publishing Research Papers."** PLOS Computational Biology 2014. See `writing guides/2014-01-15-Manuscript-preparation.md`.
- Ecarnot et al. **"Writing a Scientific Article: A Step-by-Step Guide for Beginners."** European Geriatric Medicine 2015. See `writing guides/ecarnot2015.md`.

## Online communities

- r/MachineLearning: [[Reddit](https://www.reddit.com/r/MachineLearning/)]
- Hacker News: [[link](https://news.ycombinator.com/)]
- Papers with Code: [[LLM serving](https://paperswithcode.com/area/natural-language-processing/language-modelling)]

## Suggested reading order

If you want to read only a few things:

1. **Start here:** "The Illustrated Transformer" by Jay Alammar.
2. **Then:** "Intro to Large Language Models" by Andrej Karpathy.
3. **Then:** "Efficient Memory Management for LLM Serving with PagedAttention" (vLLM paper).
4. **Then:** The InterruptLLM paper (`paper/main.tex`).
5. **Finally:** Re-read the paper with the guided notes in [[07-reading-the-paper]].

## Check your understanding

- [ ] I know where to find the original transformer paper.
- [ ] I know where to find the vLLM paper.
- [ ] I have a resource for OS scheduling basics.
- [ ] I know which writing guides are in this repository.

## Exercises

1. Read "The Illustrated Transformer" and note 3 things you learned.
2. Skim the vLLM paper abstract and introduction. How does it relate to InterruptLLM?
3. Read one OSTEP chapter on scheduling and one on virtual memory.
4. Watch Andrej Karpathy's "Intro to Large Language Models" and summarize it in one paragraph.

> [!important]
> You do not need to read everything here. Pick the resources that fill your biggest knowledge gaps. The curriculum notes are designed to be self-contained, but these references deepen your understanding.

> [!tip]
> When reading research papers, start with the abstract, introduction, and conclusion. Only dive into methodology and results after you understand the problem and claim.
