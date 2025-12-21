# Experimental Infrastructure

This document describes the experimental infrastructure for evaluating Sensei's performance.

## Overview

The experimental infrastructure provides:

1. **Iterative Improvement Experiments**: Track how scores improve across refinement iterations
2. **Ablation Studies**: Test which components matter by disabling them
3. **Evaluation Consistency Analysis**: Measure reliability of LLM-based judging
4. **Human-LLM Alignment**: Compare Sensei scores with human researcher scores
5. **Failure Case Logging**: Explicitly expose system weaknesses
6. **Reproducible Experiment Runner**: YAML-based configuration for one-command execution

## Quick Start

### Running Experiments

```bash
# Run all experiments with main config
python experiments/run_experiments.py --config experiments/configs/main.yaml --experiment all

# Run only iteration experiments
python experiments/run_experiments.py --config experiments/configs/main.yaml --experiment iteration

# Run only ablation studies
python experiments/run_experiments.py --config experiments/configs/main.yaml --experiment ablation

# Quick test run (fewer runs)
python experiments/run_experiments.py --config experiments/configs/quick.yaml --experiment iteration
```

### Configuration

Edit `experiments/configs/main.yaml` to configure:

- `seed`: Random seed for reproducibility
- `domain`: Research domain (e.g., "AI_SAFETY")
- `num_runs`: Number of runs per experiment
- `provider`: LLM provider
- `model_name`: Specific model (null = default)
- `refine_iterations`: Number of refinement iterations
- `max_papers`: Maximum papers to analyze

## Experiment Types

### 1. Iterative Improvement Experiments

**Goal**: Demonstrate that the judge-refiner loop improves idea quality over iterations.

**What it does**:
- Runs N experiments (default: 10)
- Tracks evaluation scores at each iteration
- Generates plots showing score improvement over iterations
- Logs all iterations to CSV and JSONL

**Outputs**:
- `results/csv/iteration_experiment_*.csv`: Per-iteration scores
- `results/jsonl/iteration_experiment_*.jsonl`: Full run data
- `results/plots/iteration_experiment_score_vs_iteration.png`: Mean score vs iteration
- `results/plots/iteration_experiment_passrate_vs_iteration.png`: Pass rate vs iteration

**Example**:
```python
from experiments.experiment_runner import ExperimentRunner
from src.config import ResearchDomain

runner = ExperimentRunner(seed=42)
runs = runner.run_iteration_experiment(
    domain=ResearchDomain.AI_SAFETY,
    num_runs=10,
    provider="google",
    refine_iterations=2
)
runner.save_runs(runs, "my_experiment")
runner.generate_iteration_plots(runs, "my_experiment")
```

### 2. Ablation Studies

**Goal**: Show which components matter by disabling them systematically.

**Ablations tested**:
- `disable_refiner`: Single-shot generation (no refinement)
- `disable_limitation_extraction`: Generate ideas without paper limitations
- `disable_judge_feedback_conditioning`: Refine without judge feedback

**What it does**:
- Runs baseline (all components enabled)
- Runs each ablation configuration
- Compares mean scores, pass rates, and iterations
- Performs statistical tests (t-test, Cohen's d)

**Outputs**:
- `results/tables/ablation_comparison.csv`: Comparison table
- Statistical test results in logs

**Example**:
```python
from experiments.ablation_studies import AblationStudy
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner(seed=42)
study = AblationStudy()
results = study.run_ablation_study(
    runner=runner,
    domain=ResearchDomain.AI_SAFETY,
    num_runs=10
)
comparison_df = study.generate_comparison_table(results)
```

### 3. Evaluation Consistency Analysis

**Goal**: Measure reliability of LLM-based judging by re-evaluating the same idea multiple times.

**What it does**:
- Evaluates the same idea N times (default: 10)
- Computes mean, std, variance of scores
- Generates score distribution plots
- Compares variance across different models

**Outputs**:
- `results/tables/consistency_analysis_summary.csv`: Summary statistics
- `results/csv/consistency_analysis_raw_scores.csv`: Raw scores
- `results/plots/consistency_analysis_distributions.png`: Score distributions
- `results/plots/consistency_analysis_variance_by_model.png`: Variance by model

**Example**:
```python
from experiments.evaluation_consistency import ConsistencyAnalyzer
from src.models import ResearchIdea

analyzer = ConsistencyAnalyzer()
consistency_eval = analyzer.evaluate_idea_multiple_times(
    idea=my_idea,
    idea_id="idea_1",
    num_evaluations=10,
    provider="google"
)
```

### 4. Human-LLM Alignment Evaluation

**Goal**: Measure alignment with human researchers.

**What it does**:
1. Creates template CSV with ideas for human evaluation
2. Human evaluators fill in scores (1-7)
3. Evaluates same ideas with Sensei
4. Computes correlation (Pearson, Spearman)
5. Generates scatter plot

**Workflow**:
```bash
# Step 1: Generate ideas (run iteration experiments first)
# Step 2: Create template
python -c "from experiments.human_evaluation import HumanEvaluationFramework; \
           framework = HumanEvaluationFramework(); \
           framework.create_template_csv(ideas, 'experiments/human_eval_template.csv')"

# Step 3: Human evaluators fill in scores
# Step 4: Run comparison
python -c "from experiments.human_evaluation import HumanEvaluationFramework; \
           framework = HumanEvaluationFramework(); \
           entries = framework.load_human_evaluations('experiments/human_eval_template.csv'); \
           df = framework.evaluate_with_sensei(entries); \
           correlations = framework.compute_correlations(df); \
           framework.generate_alignment_plot(df)"
```

**Outputs**:
- `results/csv/human_sensei_comparison.csv`: Comparison table
- `results/plots/human_alignment_scatter.png`: Scatter plot
- Correlation coefficients in logs

### 5. Failure Case Logging

**Goal**: Explicitly expose system weaknesses.

**Categories**:
- `refinement_decrease`: Score decreased after refinement
- `novelty_feasibility_mismatch`: High novelty but low feasibility
- `judge_disagreement`: High variance in scores across iterations
- `threshold_failure`: Never passed threshold despite iterations

**Outputs**:
- `results/failure_cases.md`: Categorized failure cases with analysis

**Example**:
```python
from experiments.failure_cases import FailureCaseLogger

logger = FailureCaseLogger()
logger.analyze_runs(runs)
logger.save_failure_cases("my_failures")
```

## Output Structure

```
experiments/results/
├── csv/              # CSV files with per-iteration data
├── jsonl/            # JSONL files with full run data
├── plots/            # PNG plots for paper
├── tables/           # CSV tables for paper
├── summary.md        # Summary report
└── failure_cases.md  # Failure case analysis
```

## Reproducibility

All experiments use:
- **Deterministic seeds**: Set via YAML config
- **Identical seeds across ablations**: Ensures fair comparison
- **Full logging**: All parameters and results logged
- **YAML configs**: Easy to reproduce exact settings

See `docs/REPRODUCIBILITY.md` for detailed reproducibility instructions.

## Expected Runtime

- **Iteration experiment** (10 runs): ~2-4 hours (depends on LLM API speed)
- **Ablation study** (4 configs × 10 runs): ~8-16 hours
- **Consistency analysis** (10 ideas × 10 evaluations): ~1-2 hours
- **Human evaluation**: Manual (human time) + ~30 min (Sensei evaluation)

## Troubleshooting

### API Rate Limits

If you hit rate limits:
- Reduce `num_runs` in config
- Use `quick.yaml` for testing
- Add delays between API calls (modify experiment_runner.py)

### Out of Memory

If you run out of memory:
- Reduce `max_papers` in config
- Process runs in batches
- Clear caches between runs

### Missing Dependencies

Install required packages:
```bash
pip install pandas numpy scipy matplotlib pyyaml
```

## Next Steps

1. Run iteration experiments to generate baseline results
2. Run ablation studies to identify important components
3. Collect human evaluations for alignment analysis
4. Review failure cases to identify improvement areas
5. Generate summary report for paper

