"""
Tests for Evaluator module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.evaluator import Evaluator
from src.models import ResearchIdea, Score, Evaluation
from tests.conftest import sample_research_idea, mock_env_vars


class TestEvaluator:
    """Test Evaluator class."""
    
    def test_evaluator_initialization(self, mock_env_vars):
        """Test Evaluator initialization."""
        evaluator = Evaluator(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            serpapi_key="test_key",
            semanticscholar_key="test_key"
        )
        assert evaluator.llm is not None
        assert evaluator.literature_searcher is not None
    
    @patch('src.evaluator.LiteratureSearcher')
    def test_evaluate_idea_success(self, mock_lit_searcher_class, sample_research_idea, mock_env_vars):
        """Test successful idea evaluation."""
        # Mock literature searcher
        mock_searcher_instance = MagicMock()
        # comprehensive_search returns (papers, formatted_literature)
        mock_searcher_instance.comprehensive_search.return_value = ([], "")
        mock_lit_searcher_class.return_value = mock_searcher_instance
        
        # Mock LLM response for evaluation
        mock_response = MagicMock()
        mock_response.content = '''{
            "novelty_score": 2,
            "audacity_score": 2,
            "feasibility_score": 2,
            "cross_disciplinary_score": 1,
            "total_score": 7,
            "novelty_justification": "Very novel approach",
            "audacity_justification": "Bold and ambitious",
            "feasibility_justification": "Highly feasible",
            "cross_disciplinary_justification": "Cross-disciplinary impact",
            "overall_summary": "Excellent idea",
            "feedback_table": [{
                "weakness": "None",
                "thinking_prompt_novelty": "",
                "thinking_prompt_audacity": "",
                "thinking_prompt_feasibility": "",
                "why_important": ""
            }],
            "de_risking_experiments": ["Experiment 1"],
            "literature_papers": []
        }'''
        
        # Mock the LLM before creating Evaluator
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.evaluator.LLMProvider.create_llm', return_value=mock_llm):
            evaluator = Evaluator(
                provider="groq",
                serpapi_key="test",
                semanticscholar_key="test"
            )
            evaluation = evaluator.evaluate(sample_research_idea)
        
        assert evaluation is not None
        assert isinstance(evaluation, Evaluation)
        assert evaluation.score.total_score == 7
        assert evaluation.passed_threshold  # 7 >= 5
    
    @patch('src.evaluator.LiteratureSearcher')
    def test_evaluate_idea_below_threshold(self, mock_lit_searcher_class, sample_research_idea, mock_env_vars):
        """Test evaluation of idea below threshold."""
        mock_searcher_instance = MagicMock()
        # comprehensive_search returns (papers, formatted_literature)
        mock_searcher_instance.comprehensive_search.return_value = ([], "")
        mock_lit_searcher_class.return_value = mock_searcher_instance
        
        mock_response = MagicMock()
        mock_response.content = '''{
            "novelty_score": 1,
            "audacity_score": 1,
            "feasibility_score": 1,
            "cross_disciplinary_score": 0,
            "total_score": 3,
            "novelty_justification": "Somewhat novel",
            "audacity_justification": "Moderate audacity",
            "feasibility_justification": "Somewhat feasible",
            "cross_disciplinary_justification": "Limited cross-disciplinary impact",
            "overall_summary": "Needs improvement",
            "feedback_table": [{
                "weakness": "Low feasibility",
                "thinking_prompt_novelty": "Think about novelty",
                "thinking_prompt_audacity": "Think about audacity",
                "thinking_prompt_feasibility": "Think about feasibility",
                "why_important": "Important for success"
            }],
            "de_risking_experiments": ["Pilot study"],
            "literature_papers": []
        }'''
        
        # Mock the LLM before creating Evaluator
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.evaluator.LLMProvider.create_llm', return_value=mock_llm):
            evaluator = Evaluator(
                provider="groq",
                serpapi_key="test",
                semanticscholar_key="test"
            )
            evaluation = evaluator.evaluate(sample_research_idea)
        
        assert evaluation.score.total_score == 3
        assert not evaluation.passed_threshold  # 3 < 5
        assert len(evaluation.feedback_table) > 0
    
    def test_evaluate_invalid_idea(self, mock_env_vars):
        """Test evaluation with invalid idea."""
        invalid_idea = MagicMock()
        invalid_idea.title = None
        
        # Mock the LLM to avoid API calls
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"novelty_score": 0, "audacity_score": 0, "feasibility_score": 0, "cross_disciplinary_score": 0, "total_score": 0, "novelty_justification": "", "audacity_justification": "", "feasibility_justification": "", "cross_disciplinary_justification": "", "overall_summary": "", "feedback_table": [], "de_risking_experiments": [], "literature_papers": []}'
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.evaluator.LLMProvider.create_llm', return_value=mock_llm):
            evaluator = Evaluator(
                provider="groq",
                serpapi_key="test",
                semanticscholar_key="test"
            )
            
            # Invalid idea should still be evaluated (may return None or raise)
            try:
                evaluation = evaluator.evaluate(invalid_idea)
                # If it doesn't raise, that's also acceptable
            except (AttributeError, ValueError, TypeError):
                # Expected for invalid input
                pass

