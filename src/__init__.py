"""
Sheldon Cooper - Autonomous Research Scientist

Main package for the autonomous research scientist system.
"""

__version__ = "0.1.0"

from .harvester import Harvester
from .autopsy import Autopsy
from .synthesizer import Synthesizer
from .evaluator import Evaluator
from .refiner import Refiner
from .reporter import Reporter
from .models import (
    Paper,
    PaperAnalysis,
    ResearchIdea,
    Score,
    ValidationFeedback,
    Evaluation,
)

__all__ = [
    "Harvester",
    "Autopsy",
    "Synthesizer",
    "Evaluator",
    "Refiner",
    "Reporter",
    "Paper",
    "PaperAnalysis",
    "ResearchIdea",
    "Score",
    "ValidationFeedback",
    "Evaluation",
]

