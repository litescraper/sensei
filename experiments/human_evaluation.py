"""
Human evaluation framework.

Compares Sensei scores with human researcher scores.
"""
import logging
import csv
from pathlib import Path
from typing import List, Optional
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt

from src.experimental_models import HumanEvalEntry
from src.evaluator import Evaluator
from src.models import ResearchIdea

logger = logging.getLogger(__name__)


class HumanEvaluationFramework:
    """Framework for human-LLM alignment evaluation."""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "csv").mkdir(exist_ok=True)
        (self.output_dir / "plots").mkdir(exist_ok=True)
        (self.output_dir / "tables").mkdir(exist_ok=True)
    
    def create_template_csv(self, ideas: List[ResearchIdea], output_path: str = "experiments/human_eval_template.csv"):
        """
        Create template CSV for human evaluators to fill in.
        
        Args:
            ideas: List of research ideas to evaluate
            output_path: Path to save template CSV
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "idea_id",
                "title",
                "abstract",
                "human_score",
                "human_notes"
            ])
            
            for i, idea in enumerate(ideas):
                writer.writerow([
                    f"idea_{i}",
                    idea.title,
                    idea.abstract,
                    "",  # Human evaluator fills this (1-7)
                    ""   # Optional notes
                ])
        
        logger.info(f"Created human evaluation template at {output_path}")
        logger.info("Please fill in the 'human_score' column (1-7) and optionally 'human_notes'")
    
    def load_human_evaluations(self, csv_path: str) -> List[HumanEvalEntry]:
        """
        Load human evaluations from filled CSV.
        
        Args:
            csv_path: Path to filled CSV
        
        Returns:
            List of HumanEvalEntry objects
        """
        entries = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("human_score") or row["human_score"].strip() == "":
                    continue
                
                try:
                    human_score = float(row["human_score"])
                    if not (1 <= human_score <= 7):
                        logger.warning(f"Invalid score {human_score} for {row['idea_id']}, skipping")
                        continue
                    
                    entries.append(HumanEvalEntry(
                        idea_id=row["idea_id"],
                        title=row["title"],
                        abstract=row["abstract"],
                        human_score=human_score,
                        human_notes=row.get("human_notes", "").strip() or None
                    ))
                except ValueError:
                    logger.warning(f"Could not parse score for {row['idea_id']}, skipping")
                    continue
        
        logger.info(f"Loaded {len(entries)} human evaluations from {csv_path}")
        return entries
    
    def evaluate_with_sensei(
        self,
        human_entries: List[HumanEvalEntry],
        provider: str = "google",
        model_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Evaluate ideas with Sensei and compare with human scores.
        
        Args:
            human_entries: Human evaluation entries
            provider: LLM provider
            model_name: Model name
        
        Returns:
            DataFrame with human and Sensei scores
        """
        evaluator = Evaluator(provider=provider, model_name=model_name)
        
        rows = []
        for entry in human_entries:
            # Reconstruct idea from entry
            idea = ResearchIdea(
                title=entry.title,
                abstract=entry.abstract,
                introduction="",  # Not available in template
                method="",
                expected_results="",
                keywords=[]
            )
            
            # Evaluate with Sensei
            try:
                evaluation = evaluator.evaluate(idea)
                sensei_score = evaluation.score.total_score
            except Exception as e:
                logger.error(f"Error evaluating {entry.idea_id}: {e}")
                sensei_score = None
            
            rows.append({
                "idea_id": entry.idea_id,
                "human_score": entry.human_score,
                "sensei_score": sensei_score,
                "human_notes": entry.human_notes
            })
        
        df = pd.DataFrame(rows)
        
        # Save to CSV
        csv_path = self.output_dir / "csv" / "human_sensei_comparison.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved comparison to {csv_path}")
        
        return df
    
    def compute_correlations(self, df: pd.DataFrame) -> dict:
        """
        Compute correlation coefficients between human and Sensei scores.
        
        Args:
            df: DataFrame with human_score and sensei_score columns
        
        Returns:
            Dictionary with correlation statistics
        """
        # Filter out None scores
        valid_df = df.dropna(subset=["human_score", "sensei_score"])
        
        if len(valid_df) < 2:
            logger.warning("Not enough valid scores for correlation analysis")
            return {}
        
        human_scores = valid_df["human_score"].values
        sensei_scores = valid_df["sensei_score"].values
        
        # Pearson correlation
        pearson_r, pearson_p = pearsonr(human_scores, sensei_scores)
        
        # Spearman correlation
        spearman_r, spearman_p = spearmanr(human_scores, sensei_scores)
        
        # Mean absolute error
        mae = np.mean(np.abs(human_scores - sensei_scores))
        
        # Root mean squared error
        rmse = np.sqrt(np.mean((human_scores - sensei_scores) ** 2))
        
        results = {
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "spearman_r": float(spearman_r),
            "spearman_p": float(spearman_p),
            "mae": float(mae),
            "rmse": float(rmse),
            "n": len(valid_df)
        }
        
        logger.info(f"Correlation results: Pearson r={pearson_r:.3f} (p={pearson_p:.3f}), "
                   f"Spearman r={spearman_r:.3f} (p={spearman_p:.3f}), MAE={mae:.3f}, RMSE={rmse:.3f}")
        
        return results
    
    def generate_alignment_plot(self, df: pd.DataFrame, output_name: str = "human_alignment"):
        """Generate scatter plot of human vs Sensei scores."""
        valid_df = df.dropna(subset=["human_score", "sensei_score"])
        
        if len(valid_df) == 0:
            logger.warning("No valid data for alignment plot")
            return
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        ax.scatter(valid_df["human_score"], valid_df["sensei_score"], alpha=0.6, s=100)
        
        # Add diagonal line (perfect alignment)
        min_score = min(valid_df["human_score"].min(), valid_df["sensei_score"].min())
        max_score = max(valid_df["human_score"].max(), valid_df["sensei_score"].max())
        ax.plot([min_score, max_score], [min_score, max_score], 'r--', linewidth=2, label='Perfect alignment')
        
        # Add correlation info
        correlations = self.compute_correlations(df)
        if correlations:
            ax.text(0.05, 0.95, 
                   f"Pearson r={correlations['pearson_r']:.3f}\n"
                   f"Spearman r={correlations['spearman_r']:.3f}\n"
                   f"MAE={correlations['mae']:.3f}",
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel("Human Score (1-7)")
        ax.set_ylabel("Sensei Score (1-7)")
        ax.set_title("Human-Sensei Score Alignment")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.output_dir / "plots" / f"{output_name}_scatter.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved alignment plot to {plot_path}")

