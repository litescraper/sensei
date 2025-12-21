# Sensei: Autonomous Research Scientist

> An AI-powered system that autonomously generates and evaluates novel research ideas 

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Sensei** is a production-grade system that functions as an automated research scientist, capable of:

- Harvesting recent papers from arXiv across multiple research domains
- Extracting limitations and vulnerabilities from research papers
- Synthesizing novel research ideas by intersecting limitations
- Evaluating ideas using a rigorous evaluation framework
- **Iteratively refining ideas** using "Agents as a Loop and Judge" mechanism
- Generating comprehensive research reports
- **Generating complete research project code** (experiments, architecture, benchmarks, ablations) when ideas pass evaluation

## Key Features

### Multi-Domain Research Support
- **21+ Pre-configured Domains**: AI Safety, Computer Vision, NLP, Robotics, Neuroscience, Quantum Computing, Bioinformatics, Climate Science, Materials Science, Theoretical CS, Graph Neural Networks, Reinforcement Learning, Federated Learning, Cryptography, Optimization, Causal Inference, Transfer Learning, Explainable AI, Multimodal Learning, Generative Models, Edge AI
- **Custom Domain Support**: Define your own research queries and categories
- **Natural Language Input**: Describe your research interests in natural language and the system will generate search queries automatically
- **Domain-Specific Optimization**: Tailored arxiv categories and search queries per domain

### Multi-Provider LLM Support
- **Google Gemini**: `gemini-3-flash-preview`, `gemini-3-pro-preview`, `gemini-2.5-flash`, `gemini-2.5-pro`
- **Anthropic Claude**: `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-opus`
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- **OpenRouter**: Access to 100+ models including Llama, Mistral, Qwen
- **Groq**: Ultra-fast inference with Llama, Mixtral, Gemma
- **Together AI**: Open-source models including Llama, Mistral, Gemma

### Beautiful Web UI
- **Streamlit-based Interface**: Modern, intuitive web interface
- **Real-time Progress Tracking**: Visual progress bars and status updates
- **Configuration Panel**: Easy domain, provider, and model selection
- **Results Dashboard**: View and download generated reports
- **Idea Validation**: Validate your existing research ideas using the same comprehensive evaluation framework

### Rigorous Evaluation Framework
- **7-Point Scoring Rubric**: Comprehensive evaluation across novelty, audacity, feasibility, and cross-disciplinary impact
- **Multi-Source Literature Search**: arXiv, Google Scholar, Semantic Scholar, OpenReview
- **Comprehensive Feedback**: Detailed scoring, thinking prompts, and de-risking experiments
- **Novelty Validation**: Semantic similarity checking to ensure originality
- **Agents as a Loop and Judge**: Iterative refinement mechanism where ideas are improved based on judge feedback before final evaluation

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/devadigapratham/sensei.git
cd autonomous-research-scientist

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Running the Web UI

```bash
streamlit run app.py
```

Access the interface at `http://localhost:8501`

### Command Line Usage

```bash
# Basic usage
python main.py --domain AI_SAFETY --provider google --max-papers 5

# With custom queries
python main.py --domain CUSTOM --custom-queries queries.txt --provider anthropic

# Full options
python main.py \
    --domain COMPUTER_VISION \
    --provider openrouter \
    --model-name "anthropic/claude-3.5-sonnet" \
    --max-papers 10 \
    --max-attempts 3 \
    --output-dir reports
```

### Running Experiments

For research evaluation and paper experiments:

```bash
# Run all experiments
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment all

# Run only iteration experiments
python experiments/run_experiments.py \
    --config experiments/configs/main.yaml \
    --experiment iteration

# Quick test run (fewer runs)
python experiments/run_experiments.py \
    --config experiments/configs/quick.yaml \
    --experiment iteration
```

See [Experiments Documentation](docs/EXPERIMENTS.md) for detailed instructions.

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Architecture](docs/ARCHITECTURE.md)**: System architecture and component diagrams
- **[How It Works](docs/HOW_IT_WORKS.md)**: Detailed explanation of the pipeline
- **[Theory](docs/THEORY.md)**: Theoretical foundation and methodology
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Installation Guide](docs/INSTALLATION.md)**: Step-by-step installation instructions
- **[Experiments](docs/EXPERIMENTS.md)**: Experimental infrastructure and evaluation
- **[Reproducibility](docs/REPRODUCIBILITY.md)**: Guide for reproducing results

## Architecture

The system consists of six core modules with an iterative refinement loop:

```
┌─────────────┐
│  Harvester  │ → Fetches papers from arXiv
└─────────────┘
       ↓
┌─────────────┐
│   Autopsy   │ → Extracts limitations from papers
└─────────────┘
       ↓
┌─────────────┐
│ Synthesizer │ → Generates novel research ideas
└─────────────┘
       ↓
┌─────────────┐
│  Evaluator  │ → Evaluates ideas using scoring rubric
│   (Judge)   │
└─────────────┘
       ↓
       ├─→ Pass? ──→ ┌─────────────┐
       │            │   Reporter  │ → Generates markdown reports
       │            └─────────────┘
       │
       └─→ Fail? ──→ ┌─────────────┐
                     │   Refiner   │ → Improves idea based on feedback
                     └─────────────┘
                            │
                            └─── Loop back to Evaluator (up to 2 iterations)
```

**Agents as a Loop and Judge**: The Evaluator (Judge) provides feedback on ideas. If an idea fails evaluation, the Refiner improves it based on the feedback, and the improved idea is re-evaluated. This loop continues until the idea passes or maximum iterations are reached.

## Research Domains

### Supported Domains

1. **AI Safety**: Trustworthy AI, Adversarial ML, Jailbreaking
2. **Computer Vision**: Image recognition, Object detection, Segmentation
3. **NLP**: Language models, Text generation, Multilingual NLP
4. **Robotics**: Autonomous systems, Control theory, Manipulation
5. **Neuroscience**: Computational neuroscience, Brain-computer interfaces
6. **Quantum Computing**: Quantum ML, Quantum algorithms
7. **Bioinformatics**: Protein structure, Genomics, Drug discovery
8. **Climate Science**: Climate modeling, Weather prediction
9. **Materials Science**: Materials discovery, Crystal structure
10. **Theoretical CS**: Algorithms, Complexity theory, Cryptography
11. **Custom**: User-defined queries and categories

## Configuration

### Environment Variables

Required API keys (depending on provider):

```env
# Google Gemini
GOOGLE_API_KEY=your_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=your_key

# OpenRouter
OPENROUTER_API_KEY=your_key

# Groq
GROQ_API_KEY=your_key

# Together AI
TOGETHER_API_KEY=your_key

# Optional but recommended
SERPAPI_API_KEY=your_key  # For Google Scholar search
SEMANTICSCHOLAR_API_KEY=your_key  # For Semantic Scholar API
```

### Domain Configuration

Domains are configured in `src/config.py`. To add a new domain:

```python
class ResearchDomain(Enum):
    YOUR_DOMAIN = "Your Domain Description"

DOMAIN_CATEGORIES[ResearchDomain.YOUR_DOMAIN] = ["cs.XX", "cs.YY"]
DOMAIN_QUERIES[ResearchDomain.YOUR_DOMAIN] = ["query 1", "query 2"]
```

## Evaluation Framework

The system evaluates ideas on four dimensions:

1. **Novelty (0-2 points)**: Few/no related papers, substantially new framing
2. **Audacity (0-2 points)**: Worthy of mainstream news, "I didn't realize this was possible"
3. **Feasibility (0-2 points)**: Achievable with today's resources, clear milestones
4. **Cross-Disciplinary (0-1 point)**: Bridges distant fields

**Total Score: 0-7 points**

Ideas scoring 5+ are considered publication-worthy. Ideas scoring 6+ are top-tier conference material.

## Example Output

The system generates comprehensive markdown reports including:

- Research idea title and abstract
- Detailed introduction and methodology
- Expected results
- Literature check results
- Scoring breakdown with justifications
- Feedback table with thinking prompts
- De-risking experiments
- Unanswered questions

See `reports/` directory for example outputs.

## Development

### Project Structure

```
.
├── src/
│   ├── main.py              # Main orchestration
│   ├── harvester.py         # Paper harvesting
│   ├── autopsy.py           # Limitation extraction
│   ├── synthesizer.py       # Idea generation
│   ├── evaluator.py         # Idea evaluation (Judge)
│   ├── refiner.py           # Idea refinement
│   ├── reporter.py          # Report generation
│   ├── literature_searcher.py  # Multi-source search
│   ├── llm_providers.py     # Multi-provider LLM support
│   ├── config.py            # Domain configuration
│   └── models.py            # Pydantic schemas
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── reports/                 # Generated reports
├── app.py                   # Streamlit UI
└── main.py                  # CLI entry point
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- New research domains
- Additional LLM providers
- Improved evaluation metrics
- UI enhancements
- Documentation improvements
- Performance optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Evaluation Framework**: Comprehensive scoring protocol
- **LangChain**: LLM orchestration framework
- **arXiv**: Research paper database
- **Streamlit**: Web UI framework

## Contact

For questions, issues, or contributions, please open an issue on GitHub.

## Citation

If you use this system in your research, please cite:

```bibtex
@software{sensei2025,
  title={Sensei: Autonomous Research Scientist},
  author={Prathamesh Devadiga},
  year={2025},
  url={https://github.com/devadigapratham/sensei}
}
```

---

**Note**: This system is designed to assist researchers, not replace them. Generated ideas should be carefully reviewed and validated by domain experts before pursuing.
