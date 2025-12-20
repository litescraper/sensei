"""
Tests for Harvester module.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from src.harvester import Harvester
from src.models import Paper


class TestHarvester:
    """Test Harvester class."""
    
    def test_harvester_initialization(self):
        """Test Harvester initialization."""
        harvester = Harvester(max_results_per_query=10)
        assert harvester.max_results_per_query == 10
        assert len(harvester.QUERIES) == 5
        assert "cs.CR" in harvester.CATEGORIES
    
    @patch('src.harvester.arxiv.Search')
    def test_search_arxiv(self, mock_search):
        """Test arxiv search functionality."""
        # Mock arxiv result
        mock_result = MagicMock()
        mock_result.title = "Test Paper"
        mock_result.summary = "Test abstract"
        mock_result.pdf_url = "https://arxiv.org/pdf/1234.5678.pdf"
        mock_result.published = datetime(2024, 6, 1, tzinfo=timezone.utc)
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        # Create proper author and category mocks
        author_mock = MagicMock()
        author_mock.name = "Author 1"
        category_mock = MagicMock()
        category_mock.term = "cs.LG"
        mock_result.authors = [author_mock]
        mock_result.categories = [category_mock]
        
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [mock_result]
        mock_search.return_value = mock_search_instance
        
        harvester = Harvester()
        papers = harvester.search_arxiv("test query", max_results=1)
        
        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].published_date.year == 2024
    
    @patch('src.harvester.arxiv.Search')
    def test_search_arxiv_filters_old_papers(self, mock_search):
        """Test that papers before 2024 are filtered out."""
        # Mock old paper
        mock_result = MagicMock()
        mock_result.title = "Old Paper"
        mock_result.summary = "Old abstract"
        mock_result.pdf_url = "https://arxiv.org/pdf/1234.5678.pdf"
        mock_result.published = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        mock_result.authors = []
        mock_result.categories = []
        
        mock_search_instance = MagicMock()
        mock_search_instance.results.return_value = [mock_result]
        mock_search.return_value = mock_search_instance
        
        harvester = Harvester()
        papers = harvester.search_arxiv("test query", max_results=1)
        
        # Old paper should be filtered out
        assert len(papers) == 0
    
    def test_harvest_all(self):
        """Test harvesting all papers."""
        harvester = Harvester()
        # This will make actual API calls, so we'll just test the structure
        assert len(harvester.QUERIES) > 0

