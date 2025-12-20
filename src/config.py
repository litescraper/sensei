"""
Configuration module for research domains and model providers.
"""
from typing import Dict, List, Optional
from enum import Enum


class ResearchDomain(Enum):
    """Supported research domains."""
    AI_SAFETY = "AI Safety, Trustworthy AI, Adversarial ML, Jailbreaking"
    COMPUTER_VISION = "Computer Vision, Image Recognition, Object Detection"
    NLP = "Natural Language Processing, Language Models, Text Generation"
    ROBOTICS = "Robotics, Autonomous Systems, Control Theory"
    NEUROSCIENCE = "Computational Neuroscience, Brain-Computer Interfaces"
    QUANTUM_COMPUTING = "Quantum Computing, Quantum Machine Learning"
    BIOINFORMATICS = "Bioinformatics, Computational Biology, Genomics"
    CLIMATE_SCIENCE = "Climate Science, Environmental Modeling"
    MATERIALS_SCIENCE = "Materials Science, Computational Chemistry"
    THEORETICAL_CS = "Theoretical Computer Science, Algorithms, Complexity"
    CUSTOM = "Custom Domain (user-specified queries)"


class ModelProvider(Enum):
    """Supported model providers."""
    GOOGLE_GEMINI = "google"
    ANTHROPIC_CLAUDE = "anthropic"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OPENAI = "openai"
    TOGETHER_AI = "together"


class Conference(Enum):
    """Target conferences for research ideas."""
    ICML = "ICML (International Conference on Machine Learning)"
    NEURIPS = "NeurIPS (Neural Information Processing Systems)"
    ICLR = "ICLR (International Conference on Learning Representations)"
    AAAI = "AAAI (Association for the Advancement of Artificial Intelligence)"
    ACL = "ACL (Association for Computational Linguistics)"
    CVPR = "CVPR (Computer Vision and Pattern Recognition)"
    ICCV = "ICCV (International Conference on Computer Vision)"
    ECCV = "ECCV (European Conference on Computer Vision)"
    KDD = "KDD (Knowledge Discovery and Data Mining)"
    SIGIR = "SIGIR (Special Interest Group on Information Retrieval)"
    EMNLP = "EMNLP (Empirical Methods in Natural Language Processing)"
    NAACL = "NAACL (North American Chapter of the ACL)"
    COLT = "COLT (Conference on Learning Theory)"
    AISTATS = "AISTATS (Artificial Intelligence and Statistics)"
    UAI = "UAI (Uncertainty in Artificial Intelligence)"
    GENERAL = "General (No specific conference target)"


# Domain-specific arxiv categories mapping
DOMAIN_CATEGORIES: Dict[ResearchDomain, List[str]] = {
    ResearchDomain.AI_SAFETY: ["cs.CR", "cs.LG", "cs.CL"],
    ResearchDomain.COMPUTER_VISION: ["cs.CV", "cs.LG"],
    ResearchDomain.NLP: ["cs.CL", "cs.LG", "cs.AI"],
    ResearchDomain.ROBOTICS: ["cs.RO", "cs.SY", "cs.LG"],
    ResearchDomain.NEUROSCIENCE: ["q-bio.NC", "cs.NE", "cs.LG"],
    ResearchDomain.QUANTUM_COMPUTING: ["quant-ph", "cs.ET", "cs.LG"],
    ResearchDomain.BIOINFORMATICS: ["q-bio.BM", "q-bio.GN", "cs.LG"],
    ResearchDomain.CLIMATE_SCIENCE: ["physics.ao-ph", "cs.CE", "cs.LG"],
    ResearchDomain.MATERIALS_SCIENCE: ["cond-mat", "physics.comp-ph", "cs.LG"],
    ResearchDomain.THEORETICAL_CS: ["cs.CC", "cs.DS", "cs.IT"],
    ResearchDomain.CUSTOM: ["cs.LG", "cs.AI"],  # Default fallback
}

# Domain-specific default queries
DOMAIN_QUERIES: Dict[ResearchDomain, List[str]] = {
    ResearchDomain.AI_SAFETY: [
        "LLM jailbreak attack defense",
        "adversarial examples large language models",
        "certified robustness transformers",
        "machine unlearning hallucinations",
        "universal adversarial suffixes"
    ],
    ResearchDomain.COMPUTER_VISION: [
        "object detection deep learning",
        "image segmentation transformers",
        "few-shot learning vision",
        "adversarial robustness computer vision",
        "self-supervised learning images"
    ],
    ResearchDomain.NLP: [
        "large language models reasoning",
        "multilingual language models",
        "text generation evaluation",
        "prompt engineering techniques",
        "retrieval augmented generation"
    ],
    ResearchDomain.ROBOTICS: [
        "reinforcement learning robotics",
        "sim-to-real transfer",
        "manipulation learning",
        "autonomous navigation",
        "multi-robot coordination"
    ],
    ResearchDomain.NEUROSCIENCE: [
        "neural network neuroscience",
        "brain-computer interfaces",
        "computational neuroscience models",
        "neural decoding algorithms",
        "spike neural networks"
    ],
    ResearchDomain.QUANTUM_COMPUTING: [
        "quantum machine learning",
        "quantum algorithms optimization",
        "quantum neural networks",
        "quantum error correction",
        "variational quantum circuits"
    ],
    ResearchDomain.BIOINFORMATICS: [
        "protein structure prediction",
        "genomic sequence analysis",
        "drug discovery machine learning",
        "single-cell genomics",
        "phylogenetic inference"
    ],
    ResearchDomain.CLIMATE_SCIENCE: [
        "climate modeling machine learning",
        "weather prediction deep learning",
        "carbon capture optimization",
        "renewable energy forecasting",
        "climate data analysis"
    ],
    ResearchDomain.MATERIALS_SCIENCE: [
        "materials discovery machine learning",
        "crystal structure prediction",
        "molecular property prediction",
        "high-throughput screening",
        "computational materials design"
    ],
    ResearchDomain.THEORETICAL_CS: [
        "algorithmic complexity theory",
        "approximation algorithms",
        "graph algorithms optimization",
        "distributed computing theory",
        "cryptographic protocols"
    ],
    ResearchDomain.CUSTOM: [],  # User will provide queries
}

