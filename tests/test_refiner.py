"""
Tests for Refiner module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.refiner import Refiner
from src.models import ResearchIdea, Evaluation, Score, ValidationFeedback
from tests.conftest import sample_research_idea, mock_env_vars


class TestRefiner:
    """Test Refiner class."""
    
    def test_refiner_initialization(self, mock_env_vars):
        """Test Refiner initialization."""
        refiner = Refiner(provider="groq", model_name="llama-3.3-70b-versatile")
        assert refiner.llm is not None
        assert refiner.output_parser is not None
    
    def test_refine_idea_success(self, sample_research_idea, mock_env_vars):
        """Test successful idea refinement."""
        # Create evaluation with feedback
        score = Score(
            novelty_score=1,
            audacity_score=1,
            feasibility_score=1,
            cross_disciplinary_score=0,
            total_score=3,
            novelty_justification="Needs more novelty",
            audacity_justification="Needs more audacity",
            feasibility_justification="Needs better feasibility",
            cross_disciplinary_justification="Limited impact"
        )
        
        feedback = ValidationFeedback(
            weakness="Low feasibility",
            thinking_prompt_novelty="Think about novelty",
            thinking_prompt_audacity="Think about audacity",
            thinking_prompt_feasibility="Improve feasibility details",
            why_important="Critical for success"
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[feedback],
            overall_summary="Needs improvement in feasibility",
            de_risking_experiments=["Pilot study"]
        )
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = '''{
            "title": "Improved: Novel Approach to LLM Safety",
            "abstract": "An improved approach with better feasibility details...",
            "introduction": "Building on previous work, we address feasibility...",
            "method": "We propose a method using standard datasets and clear validation...",
            "expected_results": "We expect clear, measurable results using standard metrics...",
            "keywords": ["LLM", "Safety", "Feasible", "Validation"]
        }'''
        
        # Mock the LLM before creating Refiner
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.refiner.LLMProvider.create_llm', return_value=mock_llm):
            refiner = Refiner(provider="groq")
            refined_idea = refiner.refine_idea(sample_research_idea, evaluation)
        
        assert refined_idea is not None
        assert isinstance(refined_idea, ResearchIdea)
        assert "Improved" in refined_idea.title or "Feasible" in refined_idea.keywords
    
    def test_refine_idea_no_feedback(self, sample_research_idea, mock_env_vars):
        """Test refinement with evaluation that has no feedback."""
        score = Score(
            novelty_score=2,
            audacity_score=2,
            feasibility_score=2,
            cross_disciplinary_score=1,
            total_score=7,
            novelty_justification="",
            audacity_justification="",
            feasibility_justification="",
            cross_disciplinary_justification=""
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[],
            overall_summary="Perfect idea",
            de_risking_experiments=[]
        )
        
        # Mock the LLM before creating Refiner
        mock_response = MagicMock()
        mock_response.content = '{"title": "Same Idea", "abstract": "...", "introduction": "...", "method": "...", "expected_results": "...", "keywords": []}'
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.refiner.LLMProvider.create_llm', return_value=mock_llm):
            refiner = Refiner(provider="groq")
            # Should still refine even without feedback
            refined_idea = refiner.refine_idea(sample_research_idea, evaluation)
            assert refined_idea is not None

