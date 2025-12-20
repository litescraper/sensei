"""
Tests for Reporter module.
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from src.reporter import Reporter
from src.models import (
    ResearchIdea,
    LossfunkEvaluation,
    LossfunkScore,
    ValidationFeedback,
)


class TestReporter:
    """Test Reporter class."""
    
    def test_reporter_initialization(self):
        """Test Reporter initialization."""
        reporter = Reporter()
        assert reporter is not None
    
    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        # Create test data
        idea = ResearchIdea(
            title="Test Research Idea",
            abstract="This is a test abstract",
            introduction="Test introduction",
            method="Test method",
            expected_results="Test results",
            keywords=["AI", "Safety"]
        )
        
        score = LossfunkScore(
            novelty_score=2,
            audacity_score=2,
            feasibility_score=2,
            cross_disciplinary_score=1,
            total_score=7,
            novelty_justification="Very novel",
            audacity_justification="Very audacious",
            feasibility_justification="Very feasible",
            cross_disciplinary_justification="Cross-disciplinary"
        )
        
        feedback = ValidationFeedback(
            weakness="Test weakness",
            thinking_prompt_novelty="Test novelty prompt",
            thinking_prompt_audacity="Test audacity prompt",
            thinking_prompt_feasibility="Test feasibility prompt",
            why_important="Test why important"
        )
        
        evaluation = LossfunkEvaluation(
            score=score,
            feedback_table=[feedback],
            overall_summary="Test overall summary",
            literature_summary="Found 5 papers",
            literature_papers=["[1234] Paper 1", "[5678] Paper 2"],
            unanswered_questions=["Question 1", "Question 2"],
            de_risking_experiments=["Experiment 1", "Experiment 2"]
        )
        
        reporter = Reporter()
        report = reporter.generate_markdown_report(idea, evaluation)
        
        # Check key sections are present
        assert "Test Research Idea" in report
        assert "**Total Score:** 7/7" in report
        assert "Step 0: Literature Quick-Scan" in report
        assert "Step 3: Overall Summary" in report
        assert "Step 4: Unanswered Questions" in report
        assert "Question 1" in report
        assert "Experiment 1" in report
    
    def test_save_report(self):
        """Test saving report to file."""
        idea = ResearchIdea(
            title="Test Idea",
            abstract="Test",
            introduction="Test",
            method="Test",
            expected_results="Test",
            keywords=[]
        )
        
        score = LossfunkScore(
            novelty_score=1,
            audacity_score=1,
            feasibility_score=1,
            cross_disciplinary_score=0,
            total_score=3,
            novelty_justification="",
            audacity_justification="",
            feasibility_justification="",
            cross_disciplinary_justification=""
        )
        
        evaluation = LossfunkEvaluation(
            score=score,
            feedback_table=[],
            overall_summary="Test",
            de_risking_experiments=[]
        )
        
        reporter = Reporter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = reporter.save_report(idea, evaluation, output_dir=tmpdir)
            
            assert Path(filepath).exists()
            assert filepath.endswith(".md")
            
            # Verify content
            content = Path(filepath).read_text()
            assert "Test Idea" in content

