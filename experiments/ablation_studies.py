"""
Ablation study infrastructure.

Tests which components matter by disabling them systematically.
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

from src.experimental_models import AblationConfig, ExperimentRun
from src.config import ResearchDomain
from experiments.experiment_runner import ExperimentRunner

logger = logging.getLogger(__name__)


class AblationStudy:
    """Runs ablation studies comparing different configurations."""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "tables").mkdir(exist_ok=True)
    
    def run_ablation_study(
        self,
        runner: ExperimentRunner,
        domain,
        num_runs: int = 10,
        provider: str = "google",
        model_name: Optional[str] = None,
        refine_iterations: int = 2
    ) -> Dict[str, List[ExperimentRun]]:
        """
        Run complete ablation study with all configurations.
        
        Returns:
            Dictionary mapping ablation name to list of runs
        """
        results = {}
        
        # Baseline (all components enabled)
        logger.info("Running baseline (all components enabled)...")
        baseline_runs = runner.run_iteration_experiment(
            domain=domain,
            num_runs=num_runs,
            provider=provider,
            model_name=model_name,
            ablation=AblationConfig(),  # All enabled
            refine_iterations=refine_iterations
        )
        results["baseline"] = baseline_runs
        runner.save_runs(baseline_runs, "ablation_baseline")
        
        # Ablation 1: Disable refiner
        logger.info("Running ablation: disable_refiner...")
        ablation_runs = runner.run_iteration_experiment(
            domain=domain,
            num_runs=num_runs,
            provider=provider,
            model_name=model_name,
            ablation=AblationConfig(disable_refiner=True),
            refine_iterations=0  # No refinements
        )
        results["disable_refiner"] = ablation_runs
        runner.save_runs(ablation_runs, "ablation_disable_refiner")
        
        # Ablation 2: Disable limitation extraction
        logger.info("Running ablation: disable_limitation_extraction...")
        ablation_runs = runner.run_iteration_experiment(
            domain=domain,
            num_runs=num_runs,
            provider=provider,
            model_name=model_name,
            ablation=AblationConfig(disable_limitation_extraction=True),
            refine_iterations=refine_iterations
        )
        results["disable_limitation_extraction"] = ablation_runs
        runner.save_runs(ablation_runs, "ablation_disable_limitation_extraction")
        
        # Ablation 3: Disable judge feedback conditioning
        logger.info("Running ablation: disable_judge_feedback_conditioning...")
        ablation_runs = runner.run_iteration_experiment(
            domain=domain,
            num_runs=num_runs,
            provider=provider,
            model_name=model_name,
            ablation=AblationConfig(disable_judge_feedback_conditioning=True),
            refine_iterations=refine_iterations
        )
        results["disable_judge_feedback_conditioning"] = ablation_runs
        runner.save_runs(ablation_runs, "ablation_disable_judge_feedback_conditioning")
        
        return results
    
    def generate_comparison_table(
        self,
        results: Dict[str, List[ExperimentRun]],
        output_name: str = "ablation_comparison"
    ) -> pd.DataFrame:
        """Generate comparison table of ablation results."""
        rows = []
        
        for ablation_name, runs in results.items():
            if not runs:
                continue
            
            final_scores = [run.final_score for run in runs]
            max_scores = [run.max_score for run in runs]
            pass_rates = [1.0 if run.passed_threshold else 0.0 for run in runs]
            num_iterations = [run.num_iterations for run in runs]
            
            rows.append({
                "Configuration": ablation_name,
                "Mean Final Score": np.mean(final_scores),
                "Std Final Score": np.std(final_scores),
                "Mean Max Score": np.mean(max_scores),
                "Std Max Score": np.std(max_scores),
                "Pass Rate": np.mean(pass_rates) * 100,
                "Mean Iterations": np.mean(num_iterations),
                "N": len(runs)
            })
        
        df = pd.DataFrame(rows)
        
        # Save to CSV
        csv_path = self.output_dir / "tables" / f"{output_name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved ablation comparison table to {csv_path}")
        
        return df
    
    def statistical_test(
        self,
        baseline_runs: List[ExperimentRun],
        ablation_runs: List[ExperimentRun]
    ) -> Dict[str, float]:
        """
        Perform statistical test between baseline and ablation.
        
        Returns:
            Dictionary with test statistics
        """
        baseline_scores = [run.final_score for run in baseline_runs]
        ablation_scores = [run.final_score for run in ablation_runs]
        
        # T-test
        t_stat, p_value = stats.ttest_ind(baseline_scores, ablation_scores)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(baseline_scores) - 1) * np.var(baseline_scores) +
             (len(ablation_scores) - 1) * np.var(ablation_scores)) /
            (len(baseline_scores) + len(ablation_scores) - 2)
        )
        cohens_d = (np.mean(baseline_scores) - np.mean(ablation_scores)) / pooled_std if pooled_std > 0 else 0.0
        
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "cohens_d": float(cohens_d),
            "baseline_mean": float(np.mean(baseline_scores)),
            "ablation_mean": float(np.mean(ablation_scores)),
            "baseline_std": float(np.std(baseline_scores)),
            "ablation_std": float(np.std(ablation_scores))
        }

