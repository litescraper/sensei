# API Reference

## Core Classes

### SheldonCooper

Main orchestration class for the research pipeline.

```python
from src.main import SheldonCooper
from src.config import ResearchDomain

scientist = SheldonCooper(
    domain=ResearchDomain.AI_SAFETY,
    provider="google",
    model_name="gemini-3-flash-preview",
    max_papers_to_analyze=10,
    max_idea_generation_attempts=3
)

report_path = scientist.run(output_dir="reports")
```

#### Parameters

- `domain` (ResearchDomain): Research domain to target
- `custom_queries` (List[str], optional): Custom search queries
- `provider` (str): LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
- `model_name` (str, optional): Specific model name
- `max_papers_to_analyze` (int): Maximum papers to analyze
- `max_idea_generation_attempts` (int): Maximum attempts to generate passing idea

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

