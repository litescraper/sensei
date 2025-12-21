"""
Tests for Synthesizer module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.synthesizer import Synthesizer
from src.models import PaperAnalysis, ResearchIdea
from tests.conftest import mock_env_vars


class TestSynthesizer:
    """Test Synthesizer class."""
    
    def test_synthesizer_initialization(self, mock_env_vars):
        """Test Synthesizer initialization."""
        synthesizer = Synthesizer(provider="groq", model_name="llama-3.3-70b-versatile")
        assert synthesizer.llm is not None
        assert synthesizer.output_parser is not None
    
    def test_synthesizer_with_conference_target(self, mock_env_vars):
        """Test Synthesizer with conference target."""
        synthesizer = Synthesizer(
            provider="groq",
            target_conference="NeurIPS"
        )
        assert synthesizer.target_conference == "NeurIPS"
    
    def test_generate_idea_success(self, mock_env_vars):
        """Test successful idea generation."""
        # Create sample analyses
        analyses = [
            PaperAnalysis(
                paper_title="Paper 1",
                main_contribution="Test contribution 1",
                methodology="Test method 1",
                limitations=["High computational cost"],
                future_work=["Scaling"],
                vulnerabilities=[]
            ),
            PaperAnalysis(
                paper_title="Paper 2",
                main_contribution="Test contribution 2",
                methodology="Test method 2",
                limitations=["Limited generalization"],
                future_work=["Better architectures"],
                vulnerabilities=[]
            )
        ]
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = '''{
            "title": "Novel Approach to Efficient ML",
            "abstract": "A novel approach combining efficiency and generalization.",
            "introduction": "Machine learning faces efficiency challenges...",
            "method": "We propose a new method that...",
            "expected_results": "We expect to achieve 90% efficiency...",
            "keywords": ["ML", "Efficiency", "Generalization"]
        }'''
        
        # Mock the LLM before creating Synthesizer
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.synthesizer.LLMProvider.create_llm', return_value=mock_llm):
            synthesizer = Synthesizer(provider="groq")
            idea = synthesizer.generate_idea(analyses)
        
        assert idea is not None
        assert isinstance(idea, ResearchIdea)
        assert idea.title == "Novel Approach to Efficient ML"
        assert len(idea.keywords) > 0
    
    def test_generate_idea_empty_analyses(self, mock_env_vars):
        """Test idea generation with empty analyses."""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content='{}')
        
        with patch('src.synthesizer.LLMProvider.create_llm', return_value=mock_llm):
            synthesizer = Synthesizer(provider="groq")
            # Empty analyses should raise ValueError or return None
            with pytest.raises((ValueError, AssertionError)):
                synthesizer.generate_idea([])
    
    def test_generate_idea_with_feedback(self, mock_env_vars):
        """Test idea generation with feedback from previous attempts."""
        analyses = [
            PaperAnalysis(
                paper_title="Paper 1",
                main_contribution="Test contribution",
                methodology="Test method",
                limitations=["Issue 1"],
                future_work=[],
                vulnerabilities=[]
            )
        ]
        
        feedback = "Previous idea was not feasible enough. Focus on simpler validation."
        
        mock_response = MagicMock()
        mock_response.content = '''{
            "title": "Improved Feasible Approach",
            "abstract": "A more feasible approach...",
            "introduction": "Building on previous work...",
            "method": "We use standard datasets and simple validation...",
            "expected_results": "We expect clear results...",
            "keywords": ["Feasible", "Simple"]
        }'''
        
        # Mock the LLM before creating Synthesizer
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.synthesizer.LLMProvider.create_llm', return_value=mock_llm):
            synthesizer = Synthesizer(provider="groq")
            # Set feedback as a dict (matching what the code expects)
            synthesizer.last_feedback = {
                'total_score': 3,
                'feasibility_score': 1,
                'feasibility_justification': feedback
            }
            idea = synthesizer.generate_idea(analyses)
        
        assert idea is not None
        assert "Feasible" in idea.keywords or "Simple" in idea.keywords

