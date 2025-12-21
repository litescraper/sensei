"""
Failure case logging and analysis.

Explicitly exposes weaknesses in the system.
"""
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.experimental_models import FailureCase, IterationTrace, ExperimentRun
from src.models import ResearchIdea, Evaluation

logger = logging.getLogger(__name__)


class FailureCaseLogger:
    """Logs and categorizes failure cases."""
    
    def __init__(self, output_dir: str = "experiments/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.failure_cases: List[FailureCase] = []
    
    def analyze_run_for_failures(self, run: ExperimentRun) -> List[FailureCase]:
        """
        Analyze a single run for failure cases.
        
        Categories:
        - refinement_decrease: Score decreased after refinement
        - novelty_feasibility_mismatch: High novelty but low feasibility
        - judge_disagreement: High variance in scores across iterations
        - threshold_failure: Never passed threshold despite iterations
        """
        failures = []
        
        if len(run.iterations) < 2:
            return failures
        
        # Check for refinement decrease
        for i in range(1, len(run.iterations)):
            prev_score = run.iterations[i-1].total_score
            curr_score = run.iterations[i].total_score
            
            if curr_score < prev_score:
                failures.append(FailureCase(
                    case_id=f"{run.run_id}_refinement_decrease_iter{i}",
                    category="refinement_decrease",
                    idea=run.iterations[i].idea,
                    evaluation=run.iterations[i].evaluation,
                    iterations=run.iterations[max(0, i-1):i+1],
                    description=f"Score decreased from {prev_score} to {curr_score} after refinement iteration {i}",
                    analysis=f"Refinement may have introduced weaknesses or removed strengths. "
                            f"Previous: {run.iterations[i-1].idea.title[:100]}... "
                            f"Refined: {run.iterations[i].idea.title[:100]}..."
                ))
        
        # Check for novelty-feasibility mismatch
        final_eval = run.final_evaluation or run.iterations[-1].evaluation
        if final_eval:
            novelty = final_eval.score.novelty_score
            feasibility = final_eval.score.feasibility_score
            
            if novelty >= 1.5 and feasibility <= 0.5:
                failures.append(FailureCase(
                    case_id=f"{run.run_id}_novelty_feasibility_mismatch",
                    category="novelty_feasibility_mismatch",
                    idea=run.final_idea or run.iterations[-1].idea,
                    evaluation=final_eval,
                    iterations=run.iterations,
                    description=f"High novelty ({novelty}/2) but low feasibility ({feasibility}/2)",
                    analysis=f"The idea is novel but may be too ambitious or require unrealistic resources. "
                            f"Novelty justification: {final_eval.score.novelty_justification[:200]}... "
                            f"Feasibility justification: {final_eval.score.feasibility_justification[:200]}..."
                ))
        
        # Check for judge disagreement (high variance)
        if len(run.iterations) >= 3:
            scores = [iter_trace.total_score for iter_trace in run.iterations]
            import numpy as np
            if np.std(scores) > 1.0:  # High variance
                failures.append(FailureCase(
                    case_id=f"{run.run_id}_judge_disagreement",
                    category="judge_disagreement",
                    idea=run.final_idea or run.iterations[-1].idea,
                    evaluation=final_eval,
                    iterations=run.iterations,
                    description=f"High score variance ({np.std(scores):.2f}) across iterations",
                    analysis=f"Scores varied significantly: {scores}. This suggests inconsistent evaluation "
                            f"or that refinements are changing the idea in unpredictable ways."
                ))
        
        # Check for threshold failure
        if not run.passed_threshold and run.num_iterations >= 2:
            failures.append(FailureCase(
                case_id=f"{run.run_id}_threshold_failure",
                category="threshold_failure",
                idea=run.final_idea or run.iterations[-1].idea,
                evaluation=final_eval,
                iterations=run.iterations,
                description=f"Failed to pass threshold (score {run.final_score}/7) after {run.num_iterations} iterations",
                analysis=f"Despite {run.num_iterations} iterations, the idea never reached the passing threshold. "
                        f"Final evaluation: {final_eval.overall_summary[:300] if final_eval else 'N/A'}..."
            ))
        
        return failures
    
    def analyze_runs(self, runs: List[ExperimentRun]):
        """Analyze multiple runs for failure cases."""
        for run in runs:
            failures = self.analyze_run_for_failures(run)
            self.failure_cases.extend(failures)
        
        logger.info(f"Identified {len(self.failure_cases)} failure cases from {len(runs)} runs")
    
    def save_failure_cases(self, output_name: str = "failure_cases"):
        """Save failure cases to markdown file."""
        output_path = self.output_dir / f"{output_name}.md"
        
        with open(output_path, 'w') as f:
            f.write("# Failure Case Analysis\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total failure cases: {len(self.failure_cases)}\n\n")
            
            # Group by category
            by_category = {}
            for case in self.failure_cases:
                if case.category not in by_category:
                    by_category[case.category] = []
                by_category[case.category].append(case)
            
            for category, cases in by_category.items():
                f.write(f"## {category.replace('_', ' ').title()}\n\n")
                f.write(f"Count: {len(cases)}\n\n")
                
                for i, case in enumerate(cases, 1):
                    f.write(f"### Case {i}: {case.case_id}\n\n")
                    f.write(f"**Description**: {case.description}\n\n")
                    f.write(f"**Idea Title**: {case.idea.title}\n\n")
                    f.write(f"**Abstract**: {case.idea.abstract[:300]}...\n\n")
                    
                    if case.evaluation:
                        f.write(f"**Score**: {case.evaluation.score.total_score}/7\n")
                        f.write(f"- Novelty: {case.evaluation.score.novelty_score}/2\n")
                        f.write(f"- Audacity: {case.evaluation.score.audacity_score}/2\n")
                        f.write(f"- Feasibility: {case.evaluation.score.feasibility_score}/2\n")
                        f.write(f"- Cross-disciplinary: {case.evaluation.score.cross_disciplinary_score}/1\n\n")
                    
                    f.write(f"**Analysis**: {case.analysis}\n\n")
                    f.write("---\n\n")
        
        logger.info(f"Saved {len(self.failure_cases)} failure cases to {output_path}")
        return output_path

