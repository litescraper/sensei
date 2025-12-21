"""
Tests for Autopsy module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.autopsy import Autopsy
from tests.conftest import sample_paper


class TestAutopsy:
    """Test Autopsy class."""
    
    def test_autopsy_initialization(self, mock_env_vars):
        """Test Autopsy initialization."""
        autopsy = Autopsy(provider="groq", model_name="llama-3.3-70b-versatile")
        assert autopsy.llm is not None
        assert autopsy.output_parser is not None
    
    @patch('src.autopsy.fitz.open')
    @patch('src.autopsy.requests.get')
    def test_extract_limitations_success(self, mock_get, mock_fitz, sample_paper, mock_env_vars):
        """Test successful limitation extraction."""
        # Mock PDF download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"PDF content"
        mock_get.return_value = mock_response
        
        # Mock PDF parsing - fitz.open(stream=...) returns a document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This paper has limitations: computational cost is high. Future work includes scaling."
        # Make mock_doc support indexing and length
        mock_doc.__len__ = lambda x: 1
        mock_doc.__getitem__ = lambda x, i: mock_page
        mock_doc.close = MagicMock()
        # fitz.open(stream=...) directly returns the doc
        mock_fitz.return_value = mock_doc
        
        # Mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.content = '{"paper_title": "Test Paper", "main_contribution": "Test contribution", "methodology": "Test method", "limitations": ["Computational cost is high"], "future_work": ["Scaling"], "vulnerabilities": []}'
        
        # Create Autopsy and mock LLM
        autopsy = Autopsy(provider="groq")
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        
        # Directly replace the llm attribute (bypassing Pydantic validation)
        object.__setattr__(autopsy, 'llm', mock_llm)
        
        analysis = autopsy.extract_limitations(sample_paper)
        
        assert analysis is not None
        # The paper_title comes from the LLM response, which we mocked with the actual paper title
        assert analysis.paper_title == sample_paper.title
        assert len(analysis.limitations) > 0
        assert "Computational cost is high" in analysis.limitations[0]
    
    @patch('src.autopsy.requests.get')
    def test_extract_limitations_pdf_download_failure(self, mock_get, sample_paper, mock_env_vars):
        """Test handling of PDF download failure."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        autopsy = Autopsy(provider="groq")
        analysis = autopsy.extract_limitations(sample_paper)
        
        # Should return None or empty analysis on failure
        assert analysis is None
    
    def test_extract_limitations_invalid_paper(self, mock_env_vars):
        """Test extraction with invalid paper."""
        invalid_paper = MagicMock()
        invalid_paper.pdf_url = None
        
        autopsy = Autopsy(provider="groq")
        analysis = autopsy.extract_limitations(invalid_paper)
        
        assert analysis is None

