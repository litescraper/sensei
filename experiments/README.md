# Experimental Infrastructure

This directory contains the experimental infrastructure for evaluating Sensei's performance.

## Structure

```
experiments/
├── __init__.py
├── experiment_runner.py      # Iterative improvement experiments
├── ablation_studies.py       # Ablation study infrastructure
├── evaluation_consistency.py # Judge reliability analysis
├── human_evaluation.py       # Human-LLM alignment framework
├── failure_cases.py          # Failure case logging
├── run_experiments.py        # Main reproducible experiment runner
├── summary_report.py         # Summary report generator
├── configs/                  # YAML configuration files
│   ├── main.yaml            # Main experiment config
│   └── quick.yaml           # Quick test config
└── results/                  # Generated results (created at runtime)
    ├── csv/                  # CSV data files
    ├── jsonl/               # JSONL data files
    ├── plots/               # PNG plots
    ├── tables/              # CSV tables
    ├── summary.md           # Summary report
    └── failure_cases.md     # Failure analysis
```

## Quick Start

```bash
# Run all experiments
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment all

# Run only iteration experiments
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment iteration
```

## Documentation

- **[Experiments Guide](../docs/EXPERIMENTS.md)**: Detailed experiment documentation
- **[Reproducibility Guide](../docs/REPRODUCIBILITY.md)**: How to reproduce results

## Key Features

1. **Iterative Improvement**: Track scores across refinement iterations
2. **Ablation Studies**: Test component importance
3. **Consistency Analysis**: Measure judge reliability
4. **Human Alignment**: Compare with human scores
5. **Failure Logging**: Explicitly expose weaknesses
6. **Reproducibility**: YAML configs, deterministic seeds

## Expected Runtime

- Iteration experiment (10 runs): ~2-4 hours
- Ablation study (4 configs × 10 runs): ~8-16 hours
- Consistency analysis: ~1-2 hours

## Outputs

All results are saved to `experiments/results/`:

- **CSV files**: Per-iteration data
- **JSONL files**: Full run data
- **Plots**: PNG figures for paper
- **Tables**: CSV tables for paper
- **Summary**: Markdown summary report
- **Failures**: Categorized failure cases

