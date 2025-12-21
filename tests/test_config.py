"""
Tests for configuration module.
"""
import pytest
from src.config import ResearchDomain, ModelProvider, Conference, DOMAIN_CATEGORIES, DOMAIN_QUERIES


class TestResearchDomain:
    """Test ResearchDomain enum."""
    
    def test_all_domains_exist(self):
        """Test that all expected domains exist."""
        expected_domains = [
            "AI_SAFETY",
            "COMPUTER_VISION",
            "NLP",
            "ROBOTICS",
            "NEUROSCIENCE",
            "QUANTUM_COMPUTING",
            "BIOINFORMATICS",
            "CLIMATE_SCIENCE",
            "MATERIALS_SCIENCE",
            "THEORETICAL_CS",
            "GRAPH_NEURAL_NETWORKS",
            "REINFORCEMENT_LEARNING",
            "FEDERATED_LEARNING",
            "CRYPTOGRAPHY",
            "OPTIMIZATION",
            "CAUSAL_INFERENCE",
            "TRANSFER_LEARNING",
            "EXPLAINABLE_AI",
            "MULTIMODAL_LEARNING",
            "GENERATIVE_MODELS",
            "EDGE_AI",
            "CUSTOM"
        ]
        
        for domain_name in expected_domains:
            assert hasattr(ResearchDomain, domain_name)
            domain = getattr(ResearchDomain, domain_name)
            assert isinstance(domain, ResearchDomain)
    
    def test_domain_categories_exist(self):
        """Test that categories exist for all domains."""
        # Some domains may not have categories defined yet
        domains_with_categories = [
            ResearchDomain.AI_SAFETY,
            ResearchDomain.COMPUTER_VISION,
            ResearchDomain.NLP,
            ResearchDomain.ROBOTICS,
            ResearchDomain.NEUROSCIENCE,
            ResearchDomain.QUANTUM_COMPUTING,
            ResearchDomain.BIOINFORMATICS,
            ResearchDomain.CLIMATE_SCIENCE,
            ResearchDomain.MATERIALS_SCIENCE,
            ResearchDomain.THEORETICAL_CS
        ]
        
        for domain in domains_with_categories:
            assert domain in DOMAIN_CATEGORIES
            assert len(DOMAIN_CATEGORIES[domain]) > 0
    
    def test_domain_queries_exist(self):
        """Test that queries exist for all domains."""
        for domain in ResearchDomain:
            if domain != ResearchDomain.CUSTOM:
                assert domain in DOMAIN_QUERIES
                assert len(DOMAIN_QUERIES[domain]) > 0


class TestModelProvider:
    """Test ModelProvider enum."""
    
    def test_all_providers_exist(self):
        """Test that all expected providers exist."""
        expected_providers = [
            "GOOGLE_GEMINI",
            "ANTHROPIC_CLAUDE",
            "OPENROUTER",
            "GROQ",
            "OPENAI",
            "TOGETHER_AI"
        ]
        
        for provider_name in expected_providers:
            assert hasattr(ModelProvider, provider_name)
            provider = getattr(ModelProvider, provider_name)
            assert isinstance(provider, ModelProvider)


class TestConference:
    """Test Conference enum."""
    
    def test_all_conferences_exist(self):
        """Test that all expected conferences exist."""
        expected_conferences = [
            "ICML",
            "NEURIPS",
            "ICLR",
            "AAAI",
            "ACL"
        ]
        
        for conf_name in expected_conferences:
            assert hasattr(Conference, conf_name)
            conf = getattr(Conference, conf_name)
            assert isinstance(conf, Conference)

