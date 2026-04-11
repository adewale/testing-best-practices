# Fuzzy Checking (Statistical Hypothesis Testing for Stochastic Code)

Test stochastic simulations and randomized algorithms using Bayesian hypothesis
testing instead of arbitrary thresholds. Rather than asking "is this close
enough?", ask: "what's the statistical evidence for a bug versus correctness?"

## When to use

- Simulation produces random outputs (Monte Carlo, random walks, percolation)
- Algorithm uses randomness internally (shuffling, sampling, hashing)
- Bug manifests as a statistical bias, not a crash or wrong type
- Traditional assertions can't express "approximately 25% of the time"
- You need to distinguish "unlucky run" from "genuine bug"

## Why not just use tolerances?

Threshold-based checks (`assert abs(observed - 0.25) < 0.05`) have two failure
modes: too tight → flaky tests on correct code; too loose → miss real bugs.
Fuzzy checking replaces the arbitrary tolerance with a principled Bayes factor
that quantifies the evidence.

## The pattern

### Step 1: Write the simulation

Keep simulation code separate from test logic.

```python
import random

CORRECT_MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]  # left, right, up, down
BUGGY_MOVES = [[-1, 0], [1, 0], [0, -1], [0, -1]]    # left, right, up, up (!)

def random_walk(grid_size, moves):
    """Walk from center until reaching an edge. Return final position."""
    center = grid_size // 2
    x, y = center, center
    edge = grid_size - 1
    while 0 < x < edge and 0 < y < edge:
        dx, dy = random.choice(moves)
        x, y = x + dx, y + dy
    return x, y
```

### Step 2: Run many trials and count outcomes

```python
def count_left_exits(moves, num_runs=1000):
    num_left = 0
    for i in range(num_runs):
        random.seed(2000 + i)
        final_x, _ = random_walk(grid_size=11, moves=moves)
        if final_x == 0:
            num_left += 1
    return num_left, num_runs
```

### Step 3: Assert with Bayes factors

```python
from vivarium_testing_utils import FuzzyChecker

def test_unbiased_walk_exits_equally():
    """Each edge should see ~25% of exits for an unbiased walk."""
    num_left, num_runs = count_left_exits(CORRECT_MOVES)

    FuzzyChecker().fuzzy_assert_proportion(
        observed_numerator=num_left,
        observed_denominator=num_runs,
        target_proportion=0.25,
    )
```

## How `fuzzy_assert_proportion` decides

Two competing hypotheses:
- **H0 (no bug)**: observed proportion matches `target_proportion`
- **H1 (bug)**: observed proportion is drawn from a broad prior (Jeffreys beta)

The Bayes factor `BF = P(data | bug) / P(data | no bug)` determines the outcome:

| Bayes factor | Decision | Meaning |
|-------------|----------|---------|
| BF > 100 | `AssertionError` | Decisive evidence of a bug |
| BF < 0.1 | Silent pass | Substantial evidence of correctness |
| 0.1 ≤ BF ≤ 100 | Warning | Inconclusive — need more data |

## API reference

```python
FuzzyChecker().fuzzy_assert_proportion(
    observed_numerator=254,         # count of events
    observed_denominator=1000,      # total trials
    target_proportion=0.25,         # exact expected proportion
    # or target_proportion=(0.23, 0.27) for an interval
    name="left_exit_proportion",    # optional label for diagnostics
)
```

Key parameters:
- `target_proportion`: float for exact expectation, tuple for interval
- `fail_bayes_factor_cutoff`: default 100.0 (decisive evidence threshold)
- `inconclusive_bayes_factor_cutoff`: default 0.1 (substantial evidence threshold)
- `name`: optional label for identifying which assertion failed

## Sharing a checker across tests

Use a session-scoped fixture to accumulate evidence across related tests:

```python
@pytest.fixture(scope="session")
def fuzzy_checker():
    return FuzzyChecker()

def test_left_exit(fuzzy_checker):
    fuzzy_checker.fuzzy_assert_proportion(
        observed_numerator=edge_counts["left"],
        observed_denominator=num_runs,
        target_proportion=0.25,
        name="percolation_left_exit",
    )

def test_right_exit(fuzzy_checker):
    fuzzy_checker.fuzzy_assert_proportion(
        observed_numerator=edge_counts["right"],
        observed_denominator=num_runs,
        target_proportion=0.25,
        name="percolation_right_exit",
    )
```

## What it catches

Subtle statistical biases that:
- Don't crash the code
- Produce individually reasonable outputs
- Only reveal themselves in aggregate
- Would require arbitrary thresholds in conventional testing

Example: A random walk with `[left, right, up, up]` instead of
`[left, right, up, down]` — each individual walk looks plausible, but over
1,000 trials the left-exit rate drops to ~3% instead of ~25%. The Bayes factor
reaches ~10^79 — astronomically decisive evidence.

## Practical guidance

- **More trials = more power**: 100 runs may be inconclusive; 1,000 usually
  gives decisive results for real bugs
- **Seed each trial deterministically**: `random.seed(base + i)` makes failures
  reproducible while still covering the distribution
- **Use exact proportions when derivable**: `0.25` for four equally likely
  outcomes. Fall back to intervals `(0.23, 0.27)` only when the exact value
  is unknown
- **Test multiple properties**: Check all four edges of a 2D walk, not just one.
  A bug may shift probability between edges
- **Python library**: `pip install vivarium-testing-utils` provides `FuzzyChecker`
- **Keep simulation fast**: Each trial should be cheap so running 1,000+ is
  feasible in a test suite
