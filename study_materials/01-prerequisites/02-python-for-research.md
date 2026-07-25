# 02 — Python for Research

> You need to read data, compute averages, and plot results. This note covers the Python skills used in the InterruptLLM simulator.

## What you need to know

- Reading CSV files with the `csv` module
- Working with lists and dictionaries
- Basic NumPy arrays and operations
- Computing mean, standard deviation, and percentiles
- Reading and writing JSON files

## Reading data from a CSV file

The simulator loads a dataset of LLM inference requests from a CSV file.

```python
import csv

with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["Prompt_Tokens"])
```

`csv.DictReader` returns each row as a dictionary where the keys are the column names.

## Lists, dictionaries, and basic analysis

The simulator stores requests as a list of dictionaries.

```python
requests = [
    {"prompt_tokens": 100, "completion_tokens": 50, "task_type": "chat"},
    {"prompt_tokens": 2000, "completion_tokens": 500, "task_type": "summarization"},
]

# Total tokens for each request
for r in requests:
    r["total_tokens"] = r["prompt_tokens"] + r["completion_tokens"]

# Average prompt length
avg_prompt = sum(r["prompt_tokens"] for r in requests) / len(requests)
print(avg_prompt)
```

## NumPy essentials

```python
import numpy as np

latencies = np.array([10, 20, 30, 40, 100])

print("Mean:", latencies.mean())
print("Std:", latencies.std())
print("P50:", np.percentile(latencies, 50))
print("P99:", np.percentile(latencies, 99))
```

Output:

```
Mean: 40.0
Std: 35.36
P50: 30.0
P99: 88.0
```

> [!important]
> `np.percentile(latencies, 99)` gives the value below which 99% of the data falls. In the paper, **P99 latency** means "99% of requests finish faster than this value."

## Standard deviation

The simulator reports `mean ± std` because results vary slightly between runs.

```python
runs = np.array([55.1, 56.5, 56.0, 55.8, 56.2])
print(f"{runs.mean():.1f} ± {runs.std():.1f}")
```

This prints: `55.9 ± 0.5`

## Reading and writing JSON

```python
import json

# Save results
results = {"p99_latency": 56.5, "throughput": 260000}
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

# Load results
with open("results.json", "r") as f:
    loaded = json.load(f)
print(loaded["p99_latency"])
```

## Sampling and randomness

The simulator uses random seeds to make experiments reproducible.

```python
import random

random.seed(42)
print([random.random() for _ in range(3)])
```

If you run this twice, you get the same numbers.

> [!important]
> A **seed** initializes the random number generator. Using the same seed makes experiments reproducible. The paper uses `seed=42` for the workload and seeds `0–19` for the multi-run experiments.

## How this connects to InterruptLLM

Open `src/interruptllm_core.py`. You will see the same patterns:

- `csv.DictReader` loads the Kaggle trace.
- Dictionaries represent requests.
- NumPy computes statistics.
- JSON stores results.
- Random seeds control arrival-time jitter.

## Check your understanding

- [ ] I can read a CSV file and compute the average of a column.
- [ ] I can compute P50, P99, mean, and std of a NumPy array.
- [ ] I understand why `random.seed()` makes results reproducible.
- [ ] I can save and load a JSON file.

## Exercises

1. Load a CSV file and compute the mean, P50, and P99 of the `Total_Latency_ms` column.
2. Generate 100 random numbers between 0 and 1 with `seed=42`. Compute their mean and std.
3. Create a list of 5 request dictionaries with `prompt_tokens` and `completion_tokens`. Add a `total_tokens` field and compute the average.

> [!tip]
> If you are not comfortable with NumPy yet, spend an extra hour on [this NumPy quickstart](https://numpy.org/doc/stable/user/quickstart.html) before continuing.
