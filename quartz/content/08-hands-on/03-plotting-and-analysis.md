# 03 — Plotting and Analysis

> This note shows how to read the result JSON files and recreate the paper's figures.

## Result file format

The result JSON files contain aggregated metrics from multiple runs.

Example structure (simplified):

```json
{
  "phase": "phase2a",
  "load_factor": 0.76,
  "policies": {
    "FCFS": {
      "p0_p99_ms": {"mean": 263.4, "std": 9.0},
      "throughput_tok_s": {"mean": 228911, "std": 247}
    },
    "MLFQ": {
      "p0_p99_ms": {"mean": 51.4, "std": 1.4},
      "throughput_tok_s": {"mean": 228911, "std": 247}
    }
  }
}
```

## Loading results in Python

```python
import json

with open("results/local_multirun/phase2a/phase2a_results.json", "r") as f:
    phase2a = json.load(f)

print(phase2a["policies"]["MLFQ"]["p0_p99_ms"])
# Output: {"mean": 51.4, "std": 1.4}
```

## Recreating Figure 3 (P0 P99 vs. load factor)

Figure 3 shows P0 P99 latency for FCFS, Priority, and InterruptLLM across load factors.

```python
import json
import matplotlib.pyplot as plt

with open("results/local_multirun/phase4a/phase4a_results.json", "r") as f:
    data = json.load(f)

load_factors = [0.56, 0.62, 0.69, 0.79, 0.93, 1.11]

for policy in ["FCFS", "Priority", "MLFQ"]:
    means = [data["policies"][policy][lf]["p0_p99_ms"]["mean"]
             for lf in load_factors]
    stds = [data["policies"][policy][lf]["p0_p99_ms"]["std"]
            for lf in load_factors]
    plt.errorbar(load_factors, means, yerr=stds, label=policy, marker="o")

plt.xlabel("Load factor")
plt.ylabel("P0 P99 latency (ms)")
plt.legend()
plt.grid(True)
plt.show()
```

> [!tip]
> The paper uses a log scale for the y-axis in some plots. If your results span a wide range (e.g., 50–900 ms), try `plt.semilogy()`.

## Recreating a bar chart from Table II

Table II compares FCFS, Priority, and InterruptLLM at ρ=0.76.

```python
import json
import matplotlib.pyplot as plt

with open("results/local_multirun/phase2a/phase2a_results.json", "r") as f:
    data = json.load(f)

policies = ["FCFS", "Priority", "MLFQ"]
p0_p99 = [data["policies"][p]["p0_p99_ms"]["mean"] for p in policies]
errors = [data["policies"][p]["p0_p99_ms"]["std"] for p in policies]

plt.bar(policies, p0_p99, yerr=errors, capsize=5)
plt.ylabel("P0 P99 latency (ms)")
plt.title("Scheduler comparison at load factor 0.76")
plt.show()
```

## Analyzing the results

When you look at the results, ask:

1. **Does the trend match the paper?** FCFS should degrade at high load; MLFQ should stay flat.
2. **Are the absolute numbers close?** Small differences are expected due to seeds and preprocessing.
3. **What does the error bar tell you?** Small error bars mean reproducible results.
4. **What is the trade-off?** Compare P0 P99 vs. P1 P99 vs. throughput.

## Example analysis questions

- At what load factor does FCFS P0 P99 exceed 200 ms?
- At what load factor does Priority P0 P99 exceed 200 ms?
- Does MLFQ keep P0 P99 below 200 ms across all tested loads?
- How much does P1 P99 increase under MLFQ?

## How this connects to the paper

The paper's figures are the visual summary of the results. Recreating them helps you internalize the numbers.

- **Figure 3:** P0 P99 vs. load factor (from phase4a)
- **Figure 4:** Swap latency (from phase5a)
- **Table II:** Scheduler comparison at ρ=0.76 (from phase2a)
- **Table III:** Swap latency numbers (from phase5a)
- **Table IV:** Ablation (from `generate_paper_extras.py`)

## Check your understanding

- [ ] I can load a result JSON file.
- [ ] I can plot P0 P99 vs. load factor.
- [ ] I can create a bar chart comparing policies.
- [ ] I can ask analytical questions about the results.

## Exercises

1. Plot P0 P99 vs. load factor for all three policies. Add a horizontal line at 200 ms (P0 SLA target).
2. Create a bar chart of P1 P99 for FCFS, Priority, and MLFQ at ρ=0.76.
3. Compute the speedup of MLFQ over FCFS at each load factor.
4. Plot throughput vs. load factor for each policy. Do the lines overlap?

> [!important]
> Plotting is not just about making pretty figures. It is about discovering patterns in the data that tables hide.

> [!question]
> After plotting, what is the most surprising or confirming result you found? Write one sentence explaining it.
