# Reproducibility Guide

This document explains how to reproduce experimental results for Sensei.

## Requirements

### Software Dependencies

```bash
pip install pandas numpy scipy matplotlib pyyaml
```

### API Keys

Ensure the following environment variables are set (in `.env` file):

```bash
# Required for evaluation
SERPAPI_API_KEY=your_key
SEMANTICSCHOLAR_API_KEY=your_key

# Required for LLM providers (at least one)
GOOGLE_API_KEY=your_key  # For Google Gemini
ANTHROPIC_API_KEY=your_key  # For Claude
OPENAI_API_KEY=your_key  # For GPT-4
GROQ_API_KEY=your_key  # For Groq
# etc.
```

### Hardware

- **Minimum**: 4GB RAM, internet connection
- **Recommended**: 8GB+ RAM, stable internet connection
- **Compute**: All computation is done via API calls (no local GPU needed)

## Reproducing Results

### Step 1: Set Seed

Edit `experiments/configs/main.yaml`:

```yaml
seed: 42  # Use same seed for reproducibility
```

Or use command line:

```bash
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment iteration
```

The seed controls:
- Random paper selection (if applicable)
- Any random sampling in the pipeline

### Step 2: Run Experiments

```bash
# Full experiment suite
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment all

# Individual experiments
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment iteration

python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment ablation
```

### Step 3: Verify Results

Results are saved to `experiments/results/`:

- **CSV files**: `csv/iteration_experiment_*.csv`
- **JSONL files**: `jsonl/iteration_experiment_*.jsonl`
- **Plots**: `plots/*.png`
- **Tables**: `tables/*.csv`

### Step 4: Compare with Published Results

Compare your results with published numbers:

1. Check mean scores in `summary.md`
2. Compare plots with published figures
3. Verify statistical tests match

## Deterministic Components

The following are deterministic (same seed → same results):

- ✅ Paper harvesting order (if deterministic)
- ✅ Random seed initialization
- ✅ Experiment run order

The following are **non-deterministic** (may vary):

- ⚠️ LLM outputs (even with temperature=0, some non-determinism may exist)
- ⚠️ API response times
- ⚠️ Literature search results (may change over time)

## Handling Non-Determinism

### LLM Non-Determinism

Even with `temperature=0`, LLM outputs may vary slightly. To minimize:

1. Use same model version
2. Use same provider
3. Run multiple times and report mean ± std

### Literature Search Non-Determinism

Literature search results may change as new papers are published. To handle:

1. Save literature search results with each run
2. Use cached results for consistency analysis
3. Note date of literature search in results

## Reproducing Specific Results

### Reproducing Iteration Experiment

```bash
# Use exact config from paper
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment iteration
```

Expected outputs:
- Mean final score: ~X.XX ± X.XX (check paper)
- Pass rate: ~XX% (check paper)
- Plots in `results/plots/`

### Reproducing Ablation Study

```bash
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment ablation
```

Expected outputs:
- Comparison table in `results/tables/ablation_comparison.csv`
- Statistical test results in logs

### Reproducing Consistency Analysis

```python
from experiments.evaluation_consistency import ConsistencyAnalyzer
from src.models import ResearchIdea

# Load ideas from previous experiments
ideas = [...]  # Load from JSONL files

analyzer = ConsistencyAnalyzer()
results = analyzer.evaluate_multiple_ideas(
    ideas=ideas,
    idea_ids=[f"idea_{i}" for i in range(len(ideas))],
    num_evaluations_per_idea=10
)
```

## Docker (Optional)

For complete reproducibility, use Docker:

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables
ENV PYTHONHASHSEED=42

CMD ["python", "experiments/run_experiments.py", "--config", "experiments/configs/main.yaml"]
```

## Version Information

To ensure reproducibility, note:

- **Python version**: 3.9+
- **Package versions**: See `requirements.txt`
- **LLM model versions**: Note in config (e.g., `gemini-3-flash-preview`)
- **API versions**: May change over time

## Troubleshooting

### Different Results on Re-run

If results differ significantly:

1. **Check seed**: Ensure same seed is used
2. **Check model**: Ensure same model version
3. **Check API**: Ensure same provider/endpoint
4. **Check config**: Ensure same YAML config

### API Changes

If APIs change:

1. Update API keys
2. Check for breaking changes in provider SDKs
3. Update model names if deprecated
4. Re-run experiments and note differences

### Missing Data

If some runs fail:

1. Check API rate limits
2. Check API keys are valid
3. Check network connectivity
4. Re-run failed runs only (modify code to skip completed)

## Reporting Reproducibility

In your paper, report:

1. **Seed**: `seed: 42` (or whatever you used)
2. **Config**: Link to exact YAML config
3. **Model versions**: Specific model names used
4. **Date**: When experiments were run
5. **Environment**: Python version, OS, etc.

Example:

> We ran all experiments with seed 42 using the configuration in `experiments/configs/main.yaml`. Experiments were run on 2025-01-20 using Python 3.9, Google Gemini `gemini-3-flash-preview`, and SerpAPI for literature search.

