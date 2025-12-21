"""
Experiment runner for iterative improvement experiments.

Tracks evaluation scores per iteration and generates plots/tables.
"""
import os
import json
import csv
import logging
import random
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import numpy as np
import pandas as pd

from src.main import Sensei
from src.config import ResearchDomain
from src.experimental_models import IterationTrace, ExperimentRun, AblationConfig
from src.models import ResearchIdea, Evaluation

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Runs iterative improvement experiments and tracks results."""
    
    def __init__(
        self,
        output_dir: str = "experiments/results",
        seed: Optional[int] = None
    ):
        """
        Initialize experiment runner.
        
        Args:
            output_dir: Directory to save results
            seed: Random seed for reproducibility
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "csv").mkdir(exist_ok=True)
        (self.output_dir / "jsonl").mkdir(exist_ok=True)
        (self.output_dir / "plots").mkdir(exist_ok=True)
        (self.output_dir / "tables").mkdir(exist_ok=True)
        
        # Set seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            self.seed = seed
        else:
            self.seed = random.randint(0, 2**31 - 1)
            random.seed(self.seed)
            np.random.seed(self.seed)
        
        logger.info(f"Experiment runner initialized with seed: {self.seed}")
    
    def run_iteration_experiment(
        self,
        domain: ResearchDomain,
        num_runs: int = 10,
        provider: str = "google",
        model_name: Optional[str] = None,
        ablation: Optional[AblationConfig] = None,
        refine_iterations: int = 2,
        max_papers: int = 10
    ) -> List[ExperimentRun]:
        """
        Run iterative improvement experiment.
        
        Args:
            domain: Research domain
            num_runs: Number of runs per domain
            provider: LLM provider
            model_name: Model name
            ablation: Ablation configuration
            refine_iterations: Number of refinement iterations
            max_papers: Maximum papers to analyze
        
        Returns:
            List of experiment runs
        """
        ablation = ablation or AblationConfig()
        runs = []
        
        logger.info(f"Starting iteration experiment: {num_runs} runs, domain={domain.value}")
        
        for run_idx in range(num_runs):
            run_id = f"{domain.name}_{run_idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Run {run_idx + 1}/{num_runs}: {run_id}")
            
            try:
                # Initialize Sensei with ablation flags
                sensei = Sensei(
                    domain=domain,
                    provider=provider,
                    model_name=model_name,
                    max_papers_to_analyze=max_papers,
                    max_idea_generation_attempts=1  # Single attempt per run for iteration tracking
                )
                
                # Harvest and analyze papers
                papers = sensei.harvest_papers()
                if not papers:
                    logger.warning(f"Run {run_id}: No papers harvested, skipping")
                    continue
                
                analyses = sensei.analyze_papers(papers)
                if not analyses:
                    logger.warning(f"Run {run_id}: No analyses generated, skipping")
                    continue
                
                # Apply ablation: disable limitation extraction if requested
                if ablation.disable_limitation_extraction:
                    # Use empty limitations for all analyses
                    for analysis in analyses:
                        analysis.limitations = []
                        analysis.vulnerabilities = []
                        analysis.future_work = []
                
                # Generate initial idea
                idea = sensei.synthesizer.generate_idea(analyses, attempt=1)
                
                # Track iterations
                iterations = []
                current_idea = idea
                
                # Initial evaluation
                evaluation = sensei.validator.evaluate(current_idea)
                iterations.append(IterationTrace(
                    iteration_index=0,
                    run_id=run_id,
                    attempt=1,
                    idea=current_idea,
                    evaluation=evaluation
                ))
                
                # Refinement loop (if not disabled)
                if not ablation.disable_refiner and refine_iterations > 0:
                    for iter_idx in range(1, refine_iterations + 1):
                        # Check if passed threshold
                        if evaluation.passed_threshold:
                            logger.info(f"Run {run_id}: Passed threshold at iteration {iter_idx - 1}")
                            break
                        
                        # Refine idea
                        try:
                            if ablation.disable_judge_feedback_conditioning:
                                # Create minimal evaluation without feedback for conditioning
                                minimal_eval = Evaluation(
                                    score=evaluation.score,
                                    overall_summary="",
                                    feedback_table=[],
                                    literature_papers=[],
                                    literature_summary="",
                                    unanswered_questions=[],
                                    de_risking_experiments=[],
                                    passed_threshold=evaluation.passed_threshold
                                )
                                refined_idea = sensei.refiner.refine_idea(current_idea, minimal_eval)
                            else:
                                refined_idea = sensei.refiner.refine_idea(current_idea, evaluation)
                            
                            current_idea = refined_idea
                            
                            # Re-evaluate
                            evaluation = sensei.validator.evaluate(current_idea)
                            
                            iterations.append(IterationTrace(
                                iteration_index=iter_idx,
                                run_id=run_id,
                                attempt=1,
                                idea=current_idea,
                                evaluation=evaluation
                            ))
                            
                        except Exception as e:
                            logger.error(f"Run {run_id}: Error in refinement iteration {iter_idx}: {e}")
                            break
                
                # Create experiment run
                experiment_run = ExperimentRun(
                    run_id=run_id,
                    domain=domain.value,
                    provider=provider,
                    model_name=model_name,
                    seed=self.seed,
                    ablation_flags=ablation.to_dict(),
                    iterations=iterations,
                    final_idea=current_idea,
                    final_evaluation=evaluation
                )
                
                runs.append(experiment_run)
                logger.info(f"Run {run_id}: Completed with {len(iterations)} iterations, final score: {experiment_run.final_score:.2f}")
                
            except Exception as e:
                logger.error(f"Run {run_id}: Failed with error: {e}", exc_info=True)
                continue
        
        return runs
    
    def save_runs(self, runs: List[ExperimentRun], experiment_name: str):
        """Save experiment runs to CSV and JSONL."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_path = self.output_dir / "csv" / f"{experiment_name}_{timestamp}.csv"
        rows = []
        for run in runs:
            for iter_trace in run.iterations:
                rows.append({
                    "run_id": run.run_id,
                    "domain": run.domain,
                    "provider": run.provider,
                    "model_name": run.model_name or "",
                    "seed": run.seed,
                    "iteration": iter_trace.iteration_index,
                    "attempt": iter_trace.attempt,
                    "total_score": iter_trace.total_score,
                    "novelty_score": iter_trace.novelty_score,
                    "audacity_score": iter_trace.audacity_score,
                    "feasibility_score": iter_trace.feasibility_score,
                    "cross_disciplinary_score": iter_trace.cross_disciplinary_score,
                    "passed_threshold": iter_trace.passed_threshold,
                    "idea_title": iter_trace.idea.title,
                    "disable_refiner": run.ablation_flags.get("disable_refiner", False),
                    "disable_limitation_extraction": run.ablation_flags.get("disable_limitation_extraction", False),
                    "disable_judge_feedback_conditioning": run.ablation_flags.get("disable_judge_feedback_conditioning", False),
                    "timestamp": iter_trace.timestamp.isoformat()
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved CSV to {csv_path}")
        
        # Save to JSONL
        jsonl_path = self.output_dir / "jsonl" / f"{experiment_name}_{timestamp}.jsonl"
        with open(jsonl_path, 'w') as f:
            for run in runs:
                run_dict = {
                    "run_id": run.run_id,
                    "domain": run.domain,
                    "provider": run.provider,
                    "model_name": run.model_name,
                    "seed": run.seed,
                    "ablation_flags": run.ablation_flags,
                    "num_iterations": run.num_iterations,
                    "final_score": run.final_score,
                    "max_score": run.max_score,
                    "passed_threshold": run.passed_threshold,
                    "iterations": [
                        {
                            "iteration_index": iter_trace.iteration_index,
                            "total_score": iter_trace.total_score,
                            "novelty_score": iter_trace.novelty_score,
                            "audacity_score": iter_trace.audacity_score,
                            "feasibility_score": iter_trace.feasibility_score,
                            "cross_disciplinary_score": iter_trace.cross_disciplinary_score,
                            "passed_threshold": iter_trace.passed_threshold,
                            "idea_title": iter_trace.idea.title,
                            "idea_abstract": iter_trace.idea.abstract,
                            "timestamp": iter_trace.timestamp.isoformat()
                        }
                        for iter_trace in run.iterations
                    ]
                }
                f.write(json.dumps(run_dict) + "\n")
        
        logger.info(f"Saved JSONL to {jsonl_path}")
        
        return csv_path, jsonl_path
    
    def generate_iteration_plots(self, runs: List[ExperimentRun], experiment_name: str):
        """Generate plots for iteration experiments."""
        import matplotlib.pyplot as plt
        
        # Collect data
        all_scores_by_iter = {}  # iteration -> list of scores
        all_pass_rates_by_iter = {}  # iteration -> pass rate
        
        for run in runs:
            for iter_trace in run.iterations:
                iter_idx = iter_trace.iteration_index
                if iter_idx not in all_scores_by_iter:
                    all_scores_by_iter[iter_idx] = []
                    all_pass_rates_by_iter[iter_idx] = []
                
                all_scores_by_iter[iter_idx].append(iter_trace.total_score)
                all_pass_rates_by_iter[iter_idx].append(1.0 if iter_trace.passed_threshold else 0.0)
        
        # Plot 1: Mean score vs iteration
        fig, ax = plt.subplots(figsize=(8, 6))
        iterations = sorted(all_scores_by_iter.keys())
        mean_scores = [np.mean(all_scores_by_iter[i]) for i in iterations]
        std_scores = [np.std(all_scores_by_iter[i]) for i in iterations]
        
        ax.errorbar(iterations, mean_scores, yerr=std_scores, marker='o', capsize=5, capthick=2)
        ax.set_xlabel("Iteration Index")
        ax.set_ylabel("Mean Score (out of 7)")
        ax.set_title("Mean Score vs Iteration")
        ax.grid(True, alpha=0.3)
        ax.set_xticks(iterations)
        
        plt.tight_layout()
        plot_path = self.output_dir / "plots" / f"{experiment_name}_score_vs_iteration.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved plot to {plot_path}")
        
        # Plot 2: Pass rate vs iteration
        fig, ax = plt.subplots(figsize=(8, 6))
        pass_rates = [np.mean(all_pass_rates_by_iter[i]) * 100 for i in iterations]
        
        ax.plot(iterations, pass_rates, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel("Iteration Index")
        ax.set_ylabel("Pass Rate (%)")
        ax.set_title("Pass Rate (Score >= 5) vs Iteration")
        ax.grid(True, alpha=0.3)
        ax.set_xticks(iterations)
        ax.set_ylim([0, 105])
        
        plt.tight_layout()
        plot_path = self.output_dir / "plots" / f"{experiment_name}_passrate_vs_iteration.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved plot to {plot_path}")

