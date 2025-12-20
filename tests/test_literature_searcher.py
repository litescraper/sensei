"""
Tests for LiteratureSearcher module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.literature_searcher import LiteratureSearcher, LiteraturePaper


class TestLiteraturePaper:
    """Test LiteraturePaper class."""
    
    def test_literature_paper_creation(self):
        """Test creating a LiteraturePaper object."""
        paper = LiteraturePaper(
            title="Test Paper",
            source="arxiv",
            paper_id="1234.5678",
            url="https://arxiv.org/pdf/1234.5678.pdf",
            relevance_reason="Relevant to test"
        )
        assert paper.title == "Test Paper"
        assert paper.source == "arxiv"
        assert "1234.5678" in str(paper)
    
    def test_literature_paper_string_representation(self):
        """Test string representation of LiteraturePaper."""
        paper = LiteraturePaper(
            title="Test Paper",
            source="arxiv",
            paper_id="1234.5678",
            relevance_reason="Very relevant"
        )
        paper_str = str(paper)
        assert "[1234.5678]" in paper_str
        assert "Test Paper" in paper_str


class TestLiteratureSearcher:
    """Test LiteratureSearcher class."""
    
    def test_literature_searcher_initialization(self):
        """Test LiteratureSearcher initialization."""
        searcher = LiteratureSearcher()
        assert searcher.serpapi_key is None or isinstance(searcher.serpapi_key, str)
    
    @patch('src.literature_searcher.arxiv.Search')
    def test_search_arxiv(self, mock_search):
        """Test arXiv search."""
        mock_result = MagicMock()
        mock_result.title = "Test Paper"
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        mock_result.pdf_url = "https://arxiv.org/pdf/1234.5678.pdf"
        mock_result.published = MagicMock(year=2024)
        
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [mock_result]
        mock_search.return_value = mock_search_instance
        
        searcher = LiteratureSearcher()
        papers = searcher.search_arxiv("test query", max_results=1)
        
        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].source == "arxiv"
    
    @patch('src.literature_searcher.GoogleSearch')
    def test_search_google_scholar(self, mock_google_search):
        """Test Google Scholar search."""
        mock_results = {
            "organic_results": [
                {
                    "title": "Test Paper",
                    "snippet": "This is a test snippet",
                    "link": "https://scholar.google.com/test",
                    "publication_info": {"summary": "2024"}
                }
            ]
        }
        mock_search_instance = MagicMock()
        mock_search_instance.get_dict.return_value = mock_results
        mock_google_search.return_value = mock_search_instance
        
        searcher = LiteratureSearcher(serpapi_key="test_key")
        papers = searcher.search_google_scholar("test query", max_results=1)
        
        assert len(papers) == 1
        assert papers[0].source == "scholar"
    
    def test_comprehensive_search(self):
        """Test comprehensive search across all sources."""
        searcher = LiteratureSearcher()
        # This will make actual API calls if keys are available
        # For now, just test the method exists
        assert hasattr(searcher, 'comprehensive_search')

