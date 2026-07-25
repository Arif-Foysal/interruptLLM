# 01 — What Are LLMs?

> Before diving into LLM inference systems, you need to understand what a Large Language Model is and how it interacts with users.

## What is a language model?

A **language model** is a program that predicts the next word (or "token") in a sequence.

For example, given the prompt:

```
The capital of France is
```

a language model might predict:

```
Paris
```

It does this by having learned patterns from vast amounts of text during training.

## What makes an LLM "large"?

The "large" in Large Language Model refers to:

- **Many parameters** (billions or trillions of numbers that encode what the model has learned)
- **Lots of training data** (text from books, web pages, code, etc.)
- **High memory requirements** (the model itself can take tens of gigabytes)

Popular examples include GPT-4, Llama, Mistral, and Qwen.

## Tokens, not words

LLMs do not operate on raw words. They operate on **tokens**, which are small pieces of text.

```
Word:      "Hello"
Tokens:    ["He", "llo"]  (depends on the tokenizer)

Word:      "programming"
Tokens:    ["program", "ming"]
```

A single token is typically about 0.75 words on average.

> [!important]
> When the paper says "300 tok/ms," it means "300 tokens generated per millisecond." Token counts determine both work and memory.

## Autoregressive generation

Modern LLMs generate text one token at a time. After each token, they feed it back in to predict the next one.

```
Prompt: "The capital of France is"
Step 1:  "The capital of France is Paris"
Step 2:  "The capital of France is Paris,"
Step 3:  "The capital of France is Paris, the"
...
```

This loop continues until a special "end-of-sequence" token is produced or a maximum length is reached.

> [!important]
> This token-by-token process is what makes LLM inference fundamentally different from training. In training, all tokens are processed in parallel. In inference, tokens are generated sequentially.

## Inference vs. training

| Aspect | Training | Inference |
|---|---|---|
| Direction | Forward + backward pass | Forward pass only |
| Parallelism | High (all tokens at once) | Limited (tokens generated one by one) |
| Memory use | Gradients + optimizer states | KV cache + model weights |
| Goal | Update model weights | Generate useful text |

The InterruptLLM paper is about **inference serving**, not training.

## The two phases of inference

Inference has two distinct phases:

1. **Prefill:** The model reads the entire prompt and builds an internal representation.
2. **Decode:** The model generates one token at a time.

We will study these in detail in [[03-autoregressive-generation]].

## Why LLM serving is hard

Three things make LLM inference expensive at scale:

1. **Model size:** The model weights are huge (e.g., 70 GB for a 70B-parameter model in FP16).
2. **KV cache memory:** Each request needs memory that grows with sequence length.
3. **Sequential decode:** Tokens are generated one by one, so latency can be high.

InterruptLLM focuses on problem #2 and #3 in multi-tenant settings.

## How this connects to InterruptLLM

The paper assumes you already know:

- LLMs generate tokens one at a time.
- Each token requires memory (KV cache) from all previous tokens.
- A long request can generate thousands of tokens, monopolizing GPU memory.

Without this background, the problem of preemption would not make sense.

## Check your understanding

- [ ] I can explain what a language model does in one sentence.
- [ ] I understand the difference between training and inference.
- [ ] I know what a token is and why it matters.
- [ ] I can name the two phases of LLM inference.

## Exercises

1. If a document has 800 words, roughly how many tokens does it have? (Use 1 token ≈ 0.75 words.)
2. Explain why LLM inference cannot be fully parallelized like training.
3. List three reasons LLM serving is hard.

> [!tip]
> Try typing a prompt into a chatbot and watching the output appear word by word. That streaming output is the decode phase in action.
