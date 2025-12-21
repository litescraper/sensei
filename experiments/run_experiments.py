"""
Reproducible experiment runner with YAML-based configuration.

One-command execution for all experiments.
"""
import os
import yaml
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import random
import numpy as np

from src.config import ResearchDomain
from src.experimental_models import AblationConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.ablation_studies import AblationStudy
from experiments.evaluation_consistency import ConsistencyAnalyzer
from experiments.human_evaluation import HumanEvaluationFramework
from experiments.failure_cases import FailureCaseLogger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load experiment configuration from YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def set_seed(seed: Optional[int]):
    """Set random seed for reproducibility."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        logger.info(f"Set seed to {seed}")
    else:
        seed = random.randint(0, 2**31 - 1)
        random.seed(seed)
        np.random.seed(seed)
        logger.info(f"Generated random seed: {seed}")
    return seed


def run_iteration_experiment(config: Dict[str, Any], runner: ExperimentRunner):
    """Run iterative improvement experiment."""
    logger.info("=" * 80)
    logger.info("Running Iterative Improvement Experiment")
    logger.info("=" * 80)
    
    domain = ResearchDomain[config.get("domain", "AI_SAFETY")]
    num_runs = config.get("num_runs", 10)
    provider = config.get("provider", "google")
    model_name = config.get("model_name")
    refine_iterations = config.get("refine_iterations", 2)
    max_papers = config.get("max_papers", 10)
    
    runs = runner.run_iteration_experiment(
        domain=domain,
        num_runs=num_runs,
        provider=provider,
        model_name=model_name,
        refine_iterations=refine_iterations,
        max_papers=max_papers
    )
    
    runner.save_runs(runs, "iteration_experiment")
    runner.generate_iteration_plots(runs, "iteration_experiment")
    
    # Analyze failures
    failure_logger = FailureCaseLogger(runner.output_dir)
    failure_logger.analyze_runs(runs)
    failure_logger.save_failure_cases("iteration_failures")
    
    return runs


def run_ablation_study(config: Dict[str, Any], runner: ExperimentRunner):
    """Run ablation study."""
    logger.info("=" * 80)
    logger.info("Running Ablation Study")
    logger.info("=" * 80)
    
    domain = ResearchDomain[config.get("domain", "AI_SAFETY")]
    num_runs = config.get("num_runs", 10)
    provider = config.get("provider", "google")
    model_name = config.get("model_name")
    refine_iterations = config.get("refine_iterations", 2)
    
    ablation_study = AblationStudy(runner.output_dir)
    results = ablation_study.run_ablation_study(
        runner=runner,
        domain=domain,
        num_runs=num_runs,
        provider=provider,
        model_name=model_name,
        refine_iterations=refine_iterations
    )
    
    # Generate comparison table
    comparison_df = ablation_study.generate_comparison_table(results, "ablation_comparison")
    
    # Statistical tests
    if "baseline" in results and len(results["baseline"]) > 0:
        for ablation_name, ablation_runs in results.items():
            if ablation_name == "baseline" or len(ablation_runs) == 0:
                continue
            
            stats_result = ablation_study.statistical_test(
                results["baseline"],
                ablation_runs
            )
            logger.info(f"Statistical test: baseline vs {ablation_name}")
            logger.info(f"  t-statistic: {stats_result['t_statistic']:.3f}")
            logger.info(f"  p-value: {stats_result['p_value']:.3f}")
            logger.info(f"  Cohen's d: {stats_result['cohens_d']:.3f}")
    
    # Analyze failures
    all_runs = []
    for runs in results.values():
        all_runs.extend(runs)
    failure_logger = FailureCaseLogger(runner.output_dir)
    failure_logger.analyze_runs(all_runs)
    failure_logger.save_failure_cases("ablation_failures")
    
    return results


def run_consistency_analysis(config: Dict[str, Any]):
    """Run evaluation consistency analysis."""
    logger.info("=" * 80)
    logger.info("Running Evaluation Consistency Analysis")
    logger.info("=" * 80)
    
    # This would need ideas to evaluate - for now, placeholder
    # In practice, you'd load ideas from previous experiments
    logger.warning("Consistency analysis requires pre-generated ideas. "
                  "Run iteration experiments first to generate ideas.")
    
    # Placeholder - would need to be implemented with actual ideas
    analyzer = ConsistencyAnalyzer()
    # analyzer.evaluate_multiple_ideas(...)
    
    return None


def run_human_evaluation(config: Dict[str, Any]):
    """Run human evaluation framework."""
    logger.info("=" * 80)
    logger.info("Running Human Evaluation")
    logger.info("=" * 80)
    
    framework = HumanEvaluationFramework()
    
    # Check if template exists or needs to be created
    template_path = config.get("human_eval_template", "experiments/human_eval_template.csv")
    
    if not Path(template_path).exists():
        logger.warning(f"Human eval template not found at {template_path}")
        logger.info("Run iteration experiments first to generate ideas, then create template")
        return None
    
    # Load human evaluations
    human_eval_path = config.get("human_eval_csv", template_path)
    if not Path(human_eval_path).exists():
        logger.warning(f"Human eval CSV not found at {human_eval_path}")
        logger.info("Please fill in the template CSV with human scores")
        return None
    
    human_entries = framework.load_human_evaluations(human_eval_path)
    
    provider = config.get("provider", "google")
    model_name = config.get("model_name")
    
    # Evaluate with Sensei
    comparison_df = framework.evaluate_with_sensei(
        human_entries,
        provider=provider,
        model_name=model_name
    )
    
    # Compute correlations
    correlations = framework.compute_correlations(comparison_df)
    
    # Generate plot
    framework.generate_alignment_plot(comparison_df)
    
    return correlations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run reproducible experiments for Sensei"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--experiment",
        type=str,
        choices=["iteration", "ablation", "consistency", "human", "all"],
        default="all",
        help="Which experiment to run"
    )
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return 1
    
    config = load_config(str(config_path))
    
    # Set seed
    seed = set_seed(config.get("seed"))
    
    # Initialize runner
    output_dir = config.get("output_dir", "experiments/results")
    runner = ExperimentRunner(output_dir=output_dir, seed=seed)
    
    # Run experiments
    if args.experiment in ["iteration", "all"]:
        run_iteration_experiment(config, runner)
    
    if args.experiment in ["ablation", "all"]:
        run_ablation_study(config, runner)
    
    if args.experiment in ["consistency", "all"]:
        run_consistency_analysis(config)
    
    if args.experiment in ["human", "all"]:
        run_human_evaluation(config)
    
    # Generate summary report
    logger.info("=" * 80)
    logger.info("Generating Summary Report")
    logger.info("=" * 80)
    
    from experiments.summary_report import SummaryReportGenerator
    
    summary_gen = SummaryReportGenerator(output_dir)
    
    # Collect results if available
    iteration_runs = []
    ablation_results = None
    
    # Try to load from saved files (simplified - in practice, you'd pass these directly)
    # For now, just generate a basic summary
    summary_gen.generate_summary(
        iteration_runs=iteration_runs,
        ablation_results=ablation_results,
        failure_cases_path=str(Path(output_dir) / "failure_cases.md")
    )
    
    logger.info("=" * 80)
    logger.info("Experiments Complete")
    logger.info("=" * 80)
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"Summary report: {output_dir}/summary.md")
    
    return 0


if __name__ == "__main__":
    exit(main())

