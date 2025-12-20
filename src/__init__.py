"""
Sheldon Cooper - Autonomous Research Scientist

Main package for the autonomous research scientist system.
"""

__version__ = "0.1.0"

from .harvester import Harvester
from .autopsy import Autopsy
from .synthesizer import Synthesizer
from .evaluator import LossfunkEvaluator
from .reporter import Reporter
from .models import (
    Paper,
    PaperAnalysis,
    ResearchIdea,
    LossfunkScore,
    ValidationFeedback,
    LossfunkEvaluation,
)

__all__ = [
    "Harvester",
    "Autopsy",
    "Synthesizer",
    "LossfunkEvaluator",
    "Reporter",
    "Paper",
    "PaperAnalysis",
    "ResearchIdea",
    "LossfunkScore",
    "ValidationFeedback",
    "LossfunkEvaluation",
]

