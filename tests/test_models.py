"""
Tests for data models.
"""
import pytest
from datetime import datetime, timezone
from src.models import (
    Paper,
    PaperAnalysis,
    ResearchIdea,
    Score,
    ValidationFeedback,
    Evaluation,
)


class TestPaper:
    """Test Paper model."""
    
    def test_paper_creation(self):
        """Test creating a Paper object."""
        paper = Paper(
            title="Test Paper",
            abstract="This is a test abstract",
            pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
            published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            arxiv_id="1234.5678"
        )
        assert paper.title == "Test Paper"
        assert paper.arxiv_id == "1234.5678"
    
    def test_paper_optional_fields(self):
        """Test Paper with optional fields."""
        paper = Paper(
            title="Test",
            abstract="Test",
            pdf_url="https://test.com",
            published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            authors=["Author 1", "Author 2"],
            categories=["cs.LG"]
        )
        assert len(paper.authors) == 2
        assert "cs.LG" in paper.categories


class TestPaperAnalysis:
    """Test PaperAnalysis model."""
    
    def test_paper_analysis_creation(self):
        """Test creating a PaperAnalysis object."""
        analysis = PaperAnalysis(
            paper_title="Test Paper",
            limitations=["Limitation 1", "Limitation 2"],
            future_work=["Future work 1"],
            vulnerabilities=["Vulnerability 1"]
        )
        assert len(analysis.limitations) == 2
        assert len(analysis.future_work) == 1
        assert analysis.paper_title == "Test Paper"
    
    def test_paper_analysis_empty_lists(self):
        """Test PaperAnalysis with empty lists."""
        analysis = PaperAnalysis(paper_title="Test")
        assert analysis.limitations == []
        assert analysis.future_work == []
        assert analysis.vulnerabilities == []


class TestResearchIdea:
    """Test ResearchIdea model."""
    
    def test_research_idea_creation(self):
        """Test creating a ResearchIdea object."""
        idea = ResearchIdea(
            title="Test Idea",
            abstract="Test abstract",
            introduction="Test introduction",
            method="Test method",
            expected_results="Test results",
            keywords=["AI", "Safety"]
        )
        assert idea.title == "Test Idea"
        assert len(idea.keywords) == 2


class TestScore:
    """Test Score model."""
    
    def test_score_creation(self):
        """Test creating a Score object."""
        score = Score(
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
        assert score.total_score == 7
        assert score.novelty_score <= 2
    
    def test_score_validation(self):
        """Test Score validation."""
        # Should raise error for invalid scores
        with pytest.raises(Exception):
            Score(
                novelty_score=3,  # Invalid: max is 2
                audacity_score=2,
                feasibility_score=2,
                cross_disciplinary_score=1,
                total_score=8,
                novelty_justification="",
                audacity_justification="",
                feasibility_justification="",
                cross_disciplinary_justification=""
            )


class TestEvaluation:
    """Test Evaluation model."""
    
    def test_evaluation_creation(self):
        """Test creating an Evaluation object."""
        score = Score(
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
        
        feedback = ValidationFeedback(
            weakness="Test weakness",
            thinking_prompt_novelty="Test novelty prompt",
            thinking_prompt_audacity="Test audacity prompt",
            thinking_prompt_feasibility="Test feasibility prompt",
            why_important="Test why"
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[feedback],
            overall_summary="Test summary",
            de_risking_experiments=["Experiment 1"]
        )
        
        assert evaluation.score.total_score == 3
        assert len(evaluation.feedback_table) == 1
        assert not evaluation.passed_threshold  # 3 < 5

