"""
Experimental data models for tracking iterations, ablations, and evaluation consistency.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .models import ResearchIdea, Evaluation, Score


@dataclass
class IterationTrace:
    """Tracks a single iteration in the judge-refiner loop."""
    iteration_index: int  # 0 = initial, 1+ = refined
    run_id: str
    attempt: int  # Which generation attempt (1, 2, 3...)
    idea: ResearchIdea
    evaluation: Evaluation
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def total_score(self) -> float:
        return self.evaluation.score.total_score
    
    @property
    def novelty_score(self) -> float:
        return self.evaluation.score.novelty_score
    
    @property
    def audacity_score(self) -> float:
        return self.evaluation.score.audacity_score
    
    @property
    def feasibility_score(self) -> float:
        return self.evaluation.score.feasibility_score
    
    @property
    def cross_disciplinary_score(self) -> float:
        return self.evaluation.score.cross_disciplinary_score
    
    @property
    def passed_threshold(self) -> bool:
        return self.evaluation.passed_threshold


@dataclass
class ExperimentRun:
    """Complete experiment run with all iterations tracked."""
    run_id: str
    domain: str
    provider: str
    model_name: Optional[str]
    seed: Optional[int]
    ablation_flags: Dict[str, bool] = field(default_factory=dict)
    iterations: List[IterationTrace] = field(default_factory=list)
    final_idea: Optional[ResearchIdea] = None
    final_evaluation: Optional[Evaluation] = None
    timestamp: datetime = field(default_factory=datetime.now)
    token_cost: Optional[float] = None  # If available from LLM provider
    
    @property
    def max_score(self) -> float:
        if not self.iterations:
            return 0.0
        return max(iter.total_score for iter in self.iterations)
    
    @property
    def final_score(self) -> float:
        if self.final_evaluation:
            return self.final_evaluation.score.total_score
        if self.iterations:
            return self.iterations[-1].total_score
        return 0.0
    
    @property
    def num_iterations(self) -> int:
        return len(self.iterations)
    
    @property
    def passed_threshold(self) -> bool:
        if self.final_evaluation:
            return self.final_evaluation.passed_threshold
        if self.iterations:
            return self.iterations[-1].passed_threshold
        return False


@dataclass
class AblationConfig:
    """Configuration for ablation studies."""
    disable_refiner: bool = False
    disable_limitation_extraction: bool = False
    disable_judge_feedback_conditioning: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        return {
            "disable_refiner": self.disable_refiner,
            "disable_limitation_extraction": self.disable_limitation_extraction,
            "disable_judge_feedback_conditioning": self.disable_judge_feedback_conditioning,
        }


@dataclass
class ConsistencyEvaluation:
    """Multiple evaluations of the same idea for consistency analysis."""
    idea: ResearchIdea
    idea_id: str
    evaluations: List[Evaluation] = field(default_factory=list)
    model_name: str = ""
    provider: str = ""
    
    @property
    def mean_score(self) -> float:
        if not self.evaluations:
            return 0.0
        return sum(eval.score.total_score for eval in self.evaluations) / len(self.evaluations)
    
    @property
    def std_score(self) -> float:
        if len(self.evaluations) < 2:
            return 0.0
        import numpy as np
        scores = [eval.score.total_score for eval in self.evaluations]
        return float(np.std(scores))
    
    @property
    def variance(self) -> float:
        if len(self.evaluations) < 2:
            return 0.0
        import numpy as np
        scores = [eval.score.total_score for eval in self.evaluations]
        return float(np.var(scores))
    
    @property
    def min_score(self) -> float:
        if not self.evaluations:
            return 0.0
        return min(eval.score.total_score for eval in self.evaluations)
    
    @property
    def max_score(self) -> float:
        if not self.evaluations:
            return 0.0
        return max(eval.score.total_score for eval in self.evaluations)


@dataclass
class HumanEvalEntry:
    """Human evaluation entry."""
    idea_id: str
    title: str
    abstract: str
    human_score: float  # 1-7
    human_notes: Optional[str] = None


@dataclass
class FailureCase:
    """Categorized failure case for analysis."""
    case_id: str
    category: str  # "refinement_decrease", "novelty_feasibility_mismatch", "judge_disagreement", etc.
    idea: ResearchIdea
    evaluation: Optional[Evaluation] = None
    iterations: Optional[List[IterationTrace]] = None
    description: str = ""
    analysis: str = ""

