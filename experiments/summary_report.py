"""
Generate paper-ready summary reports from experiment results.
"""
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import pandas as pd

from src.experimental_models import ExperimentRun

logger = logging.getLogger(__name__)


class SummaryReportGenerator:
    """Generates paper-ready summary reports."""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary(
        self,
        iteration_runs: List[ExperimentRun],
        ablation_results: Dict[str, List[ExperimentRun]] = None,
        failure_cases_path: str = None
    ) -> str:
        """
        Generate comprehensive summary report.
        
        Args:
            iteration_runs: Results from iteration experiments
            ablation_results: Results from ablation studies
            failure_cases_path: Path to failure cases markdown file
        
        Returns:
            Markdown summary report
        """
        lines = []
        lines.append("# Sensei Experimental Results Summary\n\n")
        lines.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # Iteration experiment results
        if iteration_runs:
            lines.append("## Iterative Improvement Results\n\n")
            
            final_scores = [run.final_score for run in iteration_runs]
            max_scores = [run.max_score for run in iteration_runs]
            pass_rates = [1.0 if run.passed_threshold else 0.0 for run in iteration_runs]
            num_iterations = [run.num_iterations for run in iteration_runs]
            
            import numpy as np
            lines.append(f"- **Number of runs**: {len(iteration_runs)}\n")
            lines.append(f"- **Mean final score**: {np.mean(final_scores):.2f} ± {np.std(final_scores):.2f}\n")
            lines.append(f"- **Mean max score**: {np.mean(max_scores):.2f} ± {np.std(max_scores):.2f}\n")
            lines.append(f"- **Pass rate**: {np.mean(pass_rates) * 100:.1f}%\n")
            lines.append(f"- **Mean iterations**: {np.mean(num_iterations):.2f}\n\n")
            
            # Score improvement by iteration
            if iteration_runs:
                scores_by_iter = {}
                for run in iteration_runs:
                    for iter_trace in run.iterations:
                        iter_idx = iter_trace.iteration_index
                        if iter_idx not in scores_by_iter:
                            scores_by_iter[iter_idx] = []
                        scores_by_iter[iter_idx].append(iter_trace.total_score)
                
                lines.append("### Score by Iteration\n\n")
                lines.append("| Iteration | Mean Score | Std | N |\n")
                lines.append("|-----------|------------|-----|---|\n")
                for iter_idx in sorted(scores_by_iter.keys()):
                    scores = scores_by_iter[iter_idx]
                    lines.append(f"| {iter_idx} | {np.mean(scores):.2f} | {np.std(scores):.2f} | {len(scores)} |\n")
                lines.append("\n")
        
        # Ablation results
        if ablation_results:
            lines.append("## Ablation Study Results\n\n")
            
            for ablation_name, runs in ablation_results.items():
                if not runs:
                    continue
                
                final_scores = [run.final_score for run in runs]
                pass_rates = [1.0 if run.passed_threshold else 0.0 for run in runs]
                
                lines.append(f"### {ablation_name.replace('_', ' ').title()}\n\n")
                lines.append(f"- **Mean final score**: {np.mean(final_scores):.2f} ± {np.std(final_scores):.2f}\n")
                lines.append(f"- **Pass rate**: {np.mean(pass_rates) * 100:.1f}%\n")
                lines.append(f"- **N**: {len(runs)}\n\n")
        
        # Failure cases summary
        if failure_cases_path and Path(failure_cases_path).exists():
            lines.append("## Failure Cases Summary\n\n")
            lines.append(f"See detailed analysis in: `{failure_cases_path}`\n\n")
        
        # File locations
        lines.append("## Generated Files\n\n")
        lines.append("### Plots\n")
        lines.append("- `plots/iteration_experiment_score_vs_iteration.png`\n")
        lines.append("- `plots/iteration_experiment_passrate_vs_iteration.png`\n")
        if ablation_results:
            lines.append("- `plots/ablation_comparison.png` (if generated)\n")
        lines.append("\n")
        
        lines.append("### Tables\n")
        lines.append("- `tables/ablation_comparison.csv`\n")
        lines.append("- `csv/iteration_experiment_*.csv`\n")
        lines.append("\n")
        
        summary_text = "".join(lines)
        
        # Save to file
        summary_path = self.output_dir / "summary.md"
        with open(summary_path, 'w') as f:
            f.write(summary_text)
        
        logger.info(f"Generated summary report at {summary_path}")
        return summary_text

