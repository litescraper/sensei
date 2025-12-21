# API Reference

## Core Classes

### Sensei

Main orchestration class for the research pipeline.

```python
from src.main import Sensei
from src.config import ResearchDomain

scientist = Sensei(
    domain=ResearchDomain.AI_SAFETY,
    provider="google",
    model_name="gemini-3-flash-preview",
    max_papers_to_analyze=10,
    max_idea_generation_attempts=3
)

report_path = scientist.run(output_dir="reports")
```

#### Parameters

- `domain` (ResearchDomain): Research domain to target (21+ pre-configured domains available)
- `custom_queries` (List[str], optional): Custom search queries (can be generated from natural language input)
- `provider` (str): LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
- `model_name` (str, optional): Specific model name
- `max_papers_to_analyze` (int): Maximum papers to analyze
- `max_idea_generation_attempts` (int): Maximum attempts to generate passing idea
- `target_conference` (str, optional): Target conference for idea generation

#### Methods

- `run(output_dir: str) -> Optional[str]`: Run complete pipeline, returns report path

### Harvester

Fetches papers from arxiv.

```python
from src.harvester import Harvester
from src.config import ResearchDomain

harvester = Harvester(
    domain=ResearchDomain.COMPUTER_VISION,
    max_results_per_query=20
)

papers = harvester.harvest_all()
```

### Autopsy

Extracts limitations from papers.

```python
from src.autopsy import Autopsy

autopsy = Autopsy(
    provider="anthropic",
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.1
)

analysis = autopsy.extract_limitations(paper)
```

### Synthesizer

Generates research ideas.

```python
from src.synthesizer import Synthesizer

synthesizer = Synthesizer(
    provider="openai",
    model_name="gpt-4o",
    temperature=0.8
)

idea = synthesizer.generate_idea(analyses)
```

### Evaluator

Evaluates ideas using a comprehensive evaluation framework.

```python
from src.evaluator import Evaluator

evaluator = Evaluator(
    provider="google",
    model_name="gemini-3-flash-preview",
    temperature=0.1
)

evaluation = evaluator.evaluate(idea)
```

### Refiner

Refines research ideas based on evaluation feedback. Part of the "Agents as a Loop and Judge" mechanism.

```python
from src.refiner import Refiner

refiner = Refiner(
    provider="google",
    model_name="gemini-3-flash-preview",
    temperature=0.7
)

# Refine an idea based on evaluation feedback
refined_idea = refiner.refine_idea(idea, evaluation)
```

**Key Features**:
- Takes original idea and evaluation feedback
- Identifies weaknesses from feedback table
- Makes concrete improvements addressing each weakness
- Preserves strengths of the original idea
- Returns refined idea ready for re-evaluation

### Reporter

Generates markdown reports.

```python
from src.reporter import Reporter

reporter = Reporter()
report = reporter.generate_markdown_report(idea, evaluation)
filepath = reporter.save_report(idea, evaluation, output_dir="reports")
```

### Idea Validation

Validate user-provided research ideas using the same comprehensive evaluation framework.

```python
from src.evaluator import Evaluator
from src.models import ResearchIdea

evaluator = Evaluator(
    provider="google",
    model_name="gemini-3-flash-preview",
    serpapi_key=os.getenv("SERPAPI_API_KEY"),
    semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
)

user_idea = ResearchIdea(
    title="Your Research Idea Title",
    abstract="Abstract of your idea...",
    introduction="Introduction and background...",
    method="Proposed methodology...",
    expected_results="Expected outcomes...",
    keywords=["keyword1", "keyword2"]
)

evaluation = evaluator.evaluate(user_idea)
```

**Key Features**:
- Uses the same 7-point scoring rubric as generated ideas
- Performs multi-source literature search
- Provides detailed feedback and improvement suggestions
- Suggests de-risking experiments
- Generates comprehensive evaluation reports

### CodeGenerator

Generates complete research project code for approved ideas. Only runs when an idea passes the evaluation threshold (score >= 5/7).

```python
from src.code_generator import CodeGenerator

code_generator = CodeGenerator(
    provider="google",
    model_name="gemini-3-flash-preview",
    temperature=0.3  # Lower temperature for more deterministic code
)

# Generate project code (only if idea passed threshold)
if evaluation.passed_threshold:
    project_data = code_generator.generate_project_code(idea, evaluation)
    project_path = code_generator.save_project(
        project_data=project_data,
        idea=idea,
        output_dir="generated_projects"
    )
```

**Key Features**:
- Generates complete, working research project codebase
- Creates model/architecture implementation (PyTorch/TensorFlow)
- Generates training and evaluation scripts
- Includes experiment infrastructure (train, evaluate, benchmark, ablation)
- Creates configuration files (YAML)
- Produces documentation (README, setup instructions)
- Generates requirements.txt with dependencies
- All code is production-ready and runnable

**Generated Project Structure**:
```
project_name/
├── src/
│   ├── model.py          # Main model/architecture
│   ├── trainer.py        # Training script
│   ├── evaluator.py      # Evaluation script
│   └── utils.py          # Utilities
├── experiments/
│   ├── train.py          # Training experiment
│   ├── evaluate.py       # Evaluation experiment
│   ├── benchmark.py      # Benchmark script
│   └── ablation.py       # Ablation study
├── configs/
│   └── default.yaml      # Configuration
├── requirements.txt      # Dependencies
├── README.md            # Project documentation
├── SETUP.md             # Setup instructions
├── idea.json            # Original idea (for reference)
└── evaluation.json      # Evaluation results (for reference)
```

#### Methods

##### `generate_project_code(idea: ResearchIdea, evaluation: Evaluation, project_name: Optional[str] = None) -> Dict[str, Any]`

Generates complete research project code.

- **Args**:
  - `idea` (ResearchIdea): Approved research idea
  - `evaluation` (Evaluation): Evaluation result
  - `project_name` (Optional[str]): Name for the project (default: sanitized idea title)
- **Returns**:
  - `Dict[str, Any]`: Dictionary with project structure, README, requirements, config, etc.

##### `save_project(project_data: Dict[str, Any], idea: ResearchIdea, output_dir: str = "generated_projects", project_name: Optional[str] = None) -> str`

Saves generated project to disk.

- **Args**:
  - `project_data` (Dict[str, Any]): Generated project data from LLM
  - `idea` (ResearchIdea): Research idea
  - `output_dir` (str): Base output directory
  - `project_name` (Optional[str]): Project name (default: sanitized title)
- **Returns**:
  - `str`: Path to generated project directory

## Data Models

### Paper

```python
from src.models import Paper

paper = Paper(
    title="Research Paper Title",
    abstract="Abstract text",
    pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
    published_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
    arxiv_id="1234.5678",
    authors=["Author 1", "Author 2"],
    categories=["cs.LG", "cs.CR"]
)
```

### PaperAnalysis

```python
from src.models import PaperAnalysis

analysis = PaperAnalysis(
    paper_title="Paper Title",
    limitations=["Limitation 1", "Limitation 2"],
    future_work=["Future work 1"],
    vulnerabilities=["Vulnerability 1"]
)
```

### ResearchIdea

```python
from src.models import ResearchIdea

idea = ResearchIdea(
    title="Novel Research Idea",
    abstract="Abstract...",
    introduction="Introduction...",
    method="Method...",
    expected_results="Expected results...",
    keywords=["keyword1", "keyword2"]
)
```

### Evaluation

```python
from src.models import Evaluation, Score, ValidationFeedback

score = Score(
    novelty_score=2,
    audacity_score=2,
    feasibility_score=1,
    cross_disciplinary_score=1,
    total_score=6,
    novelty_justification="...",
    audacity_justification="...",
    feasibility_justification="...",
    cross_disciplinary_justification="..."
)

evaluation = Evaluation(
    score=score,
    feedback_table=[ValidationFeedback(...)],
    overall_summary="...",
    de_risking_experiments=["Experiment 1", "Experiment 2"]
)
```

## LLM Providers

### LLMProvider

Factory class for creating LLM instances.

```python
from src.llm_providers import LLMProvider

# Google Gemini
llm = LLMProvider.create_llm("google", model_name="gemini-3-flash-preview")

# Anthropic Claude
llm = LLMProvider.create_llm("anthropic", model_name="claude-3-5-sonnet-20241022")

# OpenAI
llm = LLMProvider.create_llm("openai", model_name="gpt-4o")

# OpenRouter
llm = LLMProvider.create_llm("openrouter", model_name="anthropic/claude-3.5-sonnet")

# Groq
llm = LLMProvider.create_llm("groq", model_name="llama-3.1-70b-versatile")

# Together AI
llm = LLMProvider.create_llm("together", model_name="meta-llama/Llama-3-70b-chat-hf")
```

## Configuration

### ResearchDomain

```python
from src.config import ResearchDomain

domains = [
    ResearchDomain.AI_SAFETY,
    ResearchDomain.COMPUTER_VISION,
    ResearchDomain.NLP,
    ResearchDomain.ROBOTICS,
    ResearchDomain.NEUROSCIENCE,
    ResearchDomain.QUANTUM_COMPUTING,
    ResearchDomain.BIOINFORMATICS,
    ResearchDomain.CLIMATE_SCIENCE,
    ResearchDomain.MATERIALS_SCIENCE,
    ResearchDomain.THEORETICAL_CS,
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
    ResearchDomain.EDGE_AI,
    ResearchDomain.CUSTOM
]
```

### Available Models

```python
from src.llm_providers import AVAILABLE_MODELS

# Get available models for a provider
models = AVAILABLE_MODELS["google"]
# ['gemini-3-flash-preview', 'gemini-3-pro-preview', ...]
```

## Error Handling

All modules raise exceptions that should be caught:

```python
try:
    papers = harvester.harvest_all()
except Exception as e:
    logger.error(f"Harvesting failed: {e}")
    # Handle error
```

## Logging

All modules use Python's logging module:

```python
import logging

logging.basicConfig(level=logging.INFO)
# Module logs will appear
```

