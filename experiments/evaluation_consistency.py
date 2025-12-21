"""
Evaluation consistency analysis.

Measures reliability of LLM-based judging by re-evaluating the same idea multiple times.
"""
import logging
import json
from pathlib import Path
from typing import List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.evaluator import Evaluator
from src.models import ResearchIdea
from src.experimental_models import ConsistencyEvaluation

logger = logging.getLogger(__name__)


class ConsistencyAnalyzer:
    """Analyzes consistency of evaluation across multiple runs."""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "csv").mkdir(exist_ok=True)
        (self.output_dir / "plots").mkdir(exist_ok=True)
        (self.output_dir / "tables").mkdir(exist_ok=True)
    
    def evaluate_idea_multiple_times(
        self,
        idea: ResearchIdea,
        idea_id: str,
        num_evaluations: int = 10,
        provider: str = "google",
        model_name: Optional[str] = None
    ) -> ConsistencyEvaluation:
        """
        Evaluate the same idea multiple times to measure consistency.
        
        Args:
            idea: Research idea to evaluate
            idea_id: Unique identifier for the idea
            num_evaluations: Number of times to evaluate
            provider: LLM provider
            model_name: Model name
        
        Returns:
            ConsistencyEvaluation with all evaluations
        """
        logger.info(f"Evaluating idea {idea_id} {num_evaluations} times...")
        
        evaluator = Evaluator(provider=provider, model_name=model_name)
        evaluations = []
        
        for i in range(num_evaluations):
            logger.info(f"Evaluation {i + 1}/{num_evaluations}...")
            try:
                evaluation = evaluator.evaluate(idea)
                evaluations.append(evaluation)
            except Exception as e:
                logger.error(f"Error in evaluation {i + 1}: {e}")
                continue
        
        return ConsistencyEvaluation(
            idea=idea,
            idea_id=idea_id,
            evaluations=evaluations,
            model_name=model_name or "default",
            provider=provider
        )
    
    def evaluate_multiple_ideas(
        self,
        ideas: List[ResearchIdea],
        idea_ids: List[str],
        num_evaluations_per_idea: int = 10,
        provider: str = "google",
        model_name: Optional[str] = None
    ) -> List[ConsistencyEvaluation]:
        """Evaluate multiple ideas multiple times each."""
        results = []
        
        for idea, idea_id in zip(ideas, idea_ids):
            consistency_eval = self.evaluate_idea_multiple_times(
                idea=idea,
                idea_id=idea_id,
                num_evaluations=num_evaluations_per_idea,
                provider=provider,
                model_name=model_name
            )
            results.append(consistency_eval)
        
        return results
    
    def save_consistency_results(
        self,
        consistency_evals: List[ConsistencyEvaluation],
        output_name: str = "consistency_analysis"
    ):
        """Save consistency evaluation results."""
        # Save summary table
        rows = []
        for eval_result in consistency_evals:
            rows.append({
                "idea_id": eval_result.idea_id,
                "model": eval_result.model_name,
                "provider": eval_result.provider,
                "mean_score": eval_result.mean_score,
                "std_score": eval_result.std_score,
                "variance": eval_result.variance,
                "min_score": eval_result.min_score,
                "max_score": eval_result.max_score,
                "num_evaluations": len(eval_result.evaluations)
            })
        
        df = pd.DataFrame(rows)
        csv_path = self.output_dir / "tables" / f"{output_name}_summary.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved consistency summary to {csv_path}")
        
        # Save raw scores
        raw_rows = []
        for eval_result in consistency_evals:
            for i, evaluation in enumerate(eval_result.evaluations):
                raw_rows.append({
                    "idea_id": eval_result.idea_id,
                    "evaluation_index": i,
                    "total_score": evaluation.score.total_score,
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score
                })
        
        raw_df = pd.DataFrame(raw_rows)
        raw_csv_path = self.output_dir / "csv" / f"{output_name}_raw_scores.csv"
        raw_df.to_csv(raw_csv_path, index=False)
        logger.info(f"Saved raw scores to {raw_csv_path}")
        
        return df, raw_df
    
    def generate_consistency_plots(
        self,
        consistency_evals: List[ConsistencyEvaluation],
        output_name: str = "consistency_analysis"
    ):
        """Generate plots for consistency analysis."""
        # Plot 1: Score distributions per idea
        fig, axes = plt.subplots(len(consistency_evals), 1, figsize=(10, 3 * len(consistency_evals)))
        if len(consistency_evals) == 1:
            axes = [axes]
        
        for ax, eval_result in zip(axes, consistency_evals):
            scores = [e.score.total_score for e in eval_result.evaluations]
            ax.hist(scores, bins=range(0, 9), edgecolor='black', alpha=0.7)
            ax.axvline(eval_result.mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {eval_result.mean_score:.2f}')
            ax.set_xlabel("Score")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Idea {eval_result.idea_id} (std={eval_result.std_score:.2f})")
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.output_dir / "plots" / f"{output_name}_distributions.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved distribution plot to {plot_path}")
        
        # Plot 2: Model vs variance
        fig, ax = plt.subplots(figsize=(8, 6))
        models = [eval_result.model_name for eval_result in consistency_evals]
        variances = [eval_result.variance for eval_result in consistency_evals]
        
        ax.bar(range(len(models)), variances)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.set_ylabel("Variance")
        ax.set_title("Evaluation Variance by Model")
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plot_path = self.output_dir / "plots" / f"{output_name}_variance_by_model.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved variance plot to {plot_path}")

