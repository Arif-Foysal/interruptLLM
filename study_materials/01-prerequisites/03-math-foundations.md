# 03 — Math Foundations

> The paper uses only a few mathematical concepts. This note explains them in plain English.

## What you need to know

- Percentiles (P50, P99)
- Mean, standard deviation, and variance
- Logarithms (for log-scale plots)
- Big-O notation
- Basic fractions and ratios

## Percentiles

A percentile tells you the value below which a given percentage of observations fall.

| Percentile | Meaning |
|---|---|
| P50 | Half of the values are below this; half are above (the median) |
| P90 | 90% of values are below this |
| P99 | 99% of values are below this |
| P99.9 | 99.9% of values are below this |

### Example

Suppose request latencies are:

```
[10, 12, 13, 15, 18, 20, 25, 30, 50, 500] ms
```

- P50 = 19 ms (median of 10 values)
- P90 = 50 ms (the 9th value, 90% of 10 = 9)
- P99 = 500 ms (the maximum in this small sample)

> [!important]
> The paper focuses on **P99 latency** because tail latency is what hurts user experience in real systems. A few very slow requests matter as much as the average.

## Mean and standard deviation

The **mean** (average) is:

$$\bar{x} = \frac{x_1 + x_2 + \cdots + x_n}{n}$$

The **standard deviation** measures how spread out the values are:

$$\sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i - \bar{x})^2}$$

In the paper, you will see numbers like:

$$56.5 \pm 1.1\text{ ms}$$

This means: the average over 20 runs was 56.5 ms, and the standard deviation was 1.1 ms.

## Ratios and speedups

A speedup of $8.8\times$ means the new system is 8.8 times faster.

$$\text{speedup} = \frac{\text{old latency}}{\text{new latency}} = \frac{499.2}{56.5} \approx 8.8$$

A reduction of $2.1\times$ means the new latency is 2.1 times lower:

$$\frac{116.7}{56.5} \approx 2.1$$

> [!tip]
> "Reduces latency by $8.8\times$" means the new latency is 1/8.8 of the old latency. It does not mean the latency is reduced by 8.8 ms.

## Logarithms and log-scale plots

A log scale is useful when values span many orders of magnitude.

- $\log_{10}(10) = 1$
- $\log_{10}(100) = 2$
- $\log_{10}(1000) = 3$

In the paper, Figure 4 (swap latency) uses a log scale on the y-axis because measured times range from 6.7 ms to 208 ms.

> [!important]
> On a log scale, equal *distance* means equal *ratio*. The distance from 10 to 100 is the same as from 100 to 1000.

## Big-O notation

Big-O describes how the cost of an algorithm grows as the input size grows.

| Notation | Meaning | Example |
|---|---|---|
| $O(1)$ | Constant time | Looking up a dictionary by key |
| $O(n)$ | Grows linearly | Scanning a list once |
| $O(n \log n)$ | Grows as $n \log n$ | Sorting a list |
| $O(n^2)$ | Grows quadratically | Nested loops over the same list |

The paper says the scheduler's per-iteration cost is dominated by sorting:

$$O(n \log n + |B|)$$

where $n$ is the number of pending requests and $|B|$ is the batch size.

> [!important]
> Big-O ignores constants. It tells you how the work *scales*, not how fast it is in absolute terms. Sorting 100 requests is fast; sorting 1,000,000 requests might be slow.

## How this connects to InterruptLLM

The paper uses these math concepts everywhere:

- P99 latency is the main metric.
- Mean ± std shows confidence intervals over multiple runs.
- Speedups ($8.8\times$, $2.1\times$) compare methods.
- Log scale plots show wide-ranging swap latencies.
- Big-O analyzes the scheduler's complexity.

## Check your understanding

- [ ] I can compute P50 and P99 of a small dataset.
- [ ] I can explain why P99 is more important than average latency for user experience.
- [ ] I can interpret $56.5 \pm 1.1$ ms.
- [ ] I can explain what $O(n \log n)$ means.
- [ ] I understand why log scales are used for wide-ranging data.

## Exercises

1. Compute P50, P90, and P99 for these latencies: `[5, 6, 7, 8, 10, 12, 15, 20, 100, 1000]` ms.
2. If old latency is 200 ms and new latency is 40 ms, what is the speedup?
3. Compute the mean and standard deviation of `[50, 52, 48, 55, 51, 53, 49, 50, 52, 50]`.
4. Explain in one sentence: what does it mean that the scheduler is $O(n \log n)$?

> [!warning]
> Do not confuse the **mean** with the **median (P50)**. The mean can be heavily skewed by a few very large values. The paper uses P99 specifically because the mean would hide the tail latency problem.
