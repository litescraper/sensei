from typing import Dict, List, Optional
from enum import Enum


class ResearchDomain(Enum):
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
    GRAPH_NEURAL_NETWORKS = "Graph Neural Networks, Network Analysis"
    REINFORCEMENT_LEARNING = "Reinforcement Learning, Multi-Agent Systems"
    FEDERATED_LEARNING = "Federated Learning, Privacy-Preserving ML"
    CRYPTOGRAPHY = "Cryptography, Security Protocols, Privacy"
    OPTIMIZATION = "Optimization Theory, Convex Optimization, Meta-Learning"
    CAUSAL_INFERENCE = "Causal Inference, Causal Discovery, Causal ML"
    TRANSFER_LEARNING = "Transfer Learning, Domain Adaptation, Few-Shot Learning"
    EXPLAINABLE_AI = "Explainable AI, Interpretability, Fairness"
    MULTIMODAL_LEARNING = "Multimodal Learning, Vision-Language Models"
    GENERATIVE_MODELS = "Generative Models, GANs, Diffusion Models, VAEs"
    EDGE_AI = "Edge AI, Mobile ML, Efficient Inference"
    CUSTOM = "Custom Domain (user-specified queries)"


class ModelProvider(Enum):
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
    ResearchDomain.GRAPH_NEURAL_NETWORKS: [
        "graph neural networks attention",
        "message passing neural networks",
        "graph representation learning",
        "dynamic graph learning",
        "heterogeneous graph networks"
    ],
    ResearchDomain.REINFORCEMENT_LEARNING: [
        "deep reinforcement learning",
        "multi-agent reinforcement learning",
        "offline reinforcement learning",
        "hierarchical reinforcement learning",
        "meta reinforcement learning"
    ],
    ResearchDomain.FEDERATED_LEARNING: [
        "federated learning privacy",
        "federated optimization algorithms",
        "federated learning communication efficiency",
        "heterogeneous federated learning",
        "federated learning security"
    ],
    ResearchDomain.CRYPTOGRAPHY: [
        "post-quantum cryptography",
        "homomorphic encryption",
        "zero-knowledge proofs",
        "secure multi-party computation",
        "privacy-preserving machine learning"
    ],
    ResearchDomain.OPTIMIZATION: [
        "convex optimization algorithms",
        "non-convex optimization",
        "meta-learning optimization",
        "gradient-free optimization",
        "distributed optimization"
    ],
    ResearchDomain.CAUSAL_INFERENCE: [
        "causal discovery algorithms",
        "causal machine learning",
        "counterfactual reasoning",
        "causal effect estimation",
        "causal representation learning"
    ],
    ResearchDomain.TRANSFER_LEARNING: [
        "domain adaptation",
        "few-shot learning",
        "meta-learning",
        "continual learning",
        "cross-domain transfer"
    ],
    ResearchDomain.EXPLAINABLE_AI: [
        "model interpretability",
        "feature attribution methods",
        "fairness in machine learning",
        "algorithmic transparency",
        "adversarial robustness interpretability"
    ],
    ResearchDomain.MULTIMODAL_LEARNING: [
        "vision-language models",
        "multimodal representation learning",
        "cross-modal retrieval",
        "multimodal fusion",
        "visual question answering"
    ],
    ResearchDomain.GENERATIVE_MODELS: [
        "generative adversarial networks",
        "diffusion models",
        "variational autoencoders",
        "autoregressive models",
        "normalizing flows"
    ],
    ResearchDomain.EDGE_AI: [
        "mobile machine learning",
        "model compression",
        "neural architecture search",
        "quantization techniques",
        "efficient inference"
    ],
    ResearchDomain.CUSTOM: [],
}

