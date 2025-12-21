"""
Integration tests for main Sensei pipeline.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.main import Sensei
from src.config import ResearchDomain
from tests.conftest import mock_env_vars


class TestSenseiIntegration:
    """Integration tests for Sensei class."""
    
    def test_sensei_initialization(self, mock_env_vars):
        """Test Sensei initialization."""
        sensei = Sensei(
            domain=ResearchDomain.AI_SAFETY,
            provider="groq",
            max_papers_to_analyze=5
        )
        
        assert sensei.domain == ResearchDomain.AI_SAFETY
        assert sensei.provider == "groq"
        assert sensei.max_papers_to_analyze == 5
        assert sensei.harvester is not None
        assert sensei.autopsy is not None
        assert sensei.synthesizer is not None
        assert sensei.validator is not None
        assert sensei.refiner is not None
        assert sensei.reporter is not None
        assert sensei.code_generator is not None
    
    def test_sensei_with_custom_queries(self, mock_env_vars):
        """Test Sensei with custom queries."""
        custom_queries = ["query1", "query2", "query3"]
        sensei = Sensei(
            domain=ResearchDomain.CUSTOM,
            custom_queries=custom_queries,
            provider="groq"
        )
        
        # Check that custom queries are set
        assert len(sensei.harvester.queries) == len(custom_queries)
        assert sensei.harvester.queries == custom_queries
    
    def test_sensei_with_conference_target(self, mock_env_vars):
        """Test Sensei with conference target."""
        sensei = Sensei(
            domain=ResearchDomain.AI_SAFETY,
            provider="groq",
            target_conference="NeurIPS"
        )
        
        assert sensei.target_conference == "NeurIPS"
        assert sensei.synthesizer.target_conference == "NeurIPS"
    
    @patch('src.main.Harvester.harvest_all')
    @patch('src.main.Autopsy.extract_limitations')
    @patch('src.main.Synthesizer.generate_idea')
    @patch('src.main.Evaluator.evaluate')
    @patch('src.main.Reporter.save_report')
    def test_sensei_run_pipeline_success(
        self,
        mock_save_report,
        mock_evaluate,
        mock_generate_idea,
        mock_extract_limitations,
        mock_harvest_all,
        mock_env_vars,
        tmp_path
    ):
        """Test successful pipeline run."""
        from datetime import datetime, timezone
        from src.models import Paper, PaperAnalysis, ResearchIdea, Evaluation, Score
        
        # Mock harvest
        mock_papers = [
            Paper(
                title="Paper 1",
                abstract="Abstract 1",
                pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
                published_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                arxiv_id="1234.5678"
            )
        ]
        mock_harvest_all.return_value = mock_papers
        
        # Mock autopsy
        mock_analysis = PaperAnalysis(
            paper_title="Paper 1",
            main_contribution="Test contribution",
            methodology="Test method",
            limitations=["Limitation 1"],
            future_work=["Future 1"],
            vulnerabilities=[]
        )
        mock_extract_limitations.return_value = mock_analysis
        
        # Mock synthesizer
        mock_idea = ResearchIdea(
            title="Test Idea",
            abstract="Test abstract",
            introduction="Test intro",
            method="Test method",
            expected_results="Test results",
            keywords=["test"]
        )
        mock_generate_idea.return_value = mock_idea
        
        # Mock evaluator
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
        mock_evaluation = Evaluation(
            score=score,
            feedback_table=[],
            overall_summary="Great",
            de_risking_experiments=[]
        )
        mock_evaluate.return_value = mock_evaluation
        
        # Mock reporter
        mock_save_report.return_value = str(tmp_path / "report.md")
        
        sensei = Sensei(
            domain=ResearchDomain.AI_SAFETY,
            provider="groq",
            max_papers_to_analyze=1,
            max_idea_generation_attempts=1
        )
        
        report_path = sensei.run(output_dir=str(tmp_path))
        
        assert report_path is not None
        assert mock_harvest_all.called
        assert mock_extract_limitations.called
        assert mock_generate_idea.called
        assert mock_evaluate.called
        assert mock_save_report.called
    
    def test_sensei_all_domains(self, mock_env_vars):
        """Test Sensei initialization with all supported domains."""
        from src.config import ResearchDomain
        
        domains = [
            ResearchDomain.AI_SAFETY,
            ResearchDomain.COMPUTER_VISION,
            ResearchDomain.NLP,
            ResearchDomain.GRAPH_NEURAL_NETWORKS,
            ResearchDomain.REINFORCEMENT_LEARNING,
            ResearchDomain.FEDERATED_LEARNING,
            ResearchDomain.CRYPTOGRAPHY,
            ResearchDomain.OPTIMIZATION,
            ResearchDomain.CAUSAL_INFERENCE,
            ResearchDomain.TRANSFER_LEARNING,
            ResearchDomain.EXPLAINABLE_AI,
            ResearchDomain.MULTIMODAL_LEARNING,
            ResearchDomain.GENERATIVE_MODELS,
            ResearchDomain.EDGE_AI
        ]
        
        for domain in domains:
            sensei = Sensei(domain=domain, provider="groq")
            assert sensei.domain == domain
            assert sensei.harvester.domain == domain

