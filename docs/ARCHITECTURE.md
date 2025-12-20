# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Autonomous Research Scientist                │
│                         (Sheldon Cooper)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │           Configuration Layer                │
        │  - Research Domain Selection                 │
        │  - LLM Provider Selection                    │
        │  - Model Selection                           │
        └─────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────┐                        ┌───────────────┐
│   Module 1    │                        │  LLM Provider │
│   Harvester   │                        │    Manager     │
│               │                        │                │
│ - arXiv API   │                        │ - Google       │
│ - Filtering   │                        │ - Anthropic    │
│ - Dedupe      │                        │ - OpenAI       │
└───────────────┘                        │ - OpenRouter  │
        │                                 │ - Groq         │
        ▼                                 │ - Together     │
┌───────────────┐                        └───────────────┘
│   Module 2    │                                 │
│   Autopsy     │                                 │
│               │                                 │
│ - PDF Parse   │                                 │
│ - LLM Extract │◄──────────────────────────────┘
│ - Limitations │
└───────────────┘
        │
        ▼
┌───────────────┐
│   Module 3    │
│  Synthesizer  │
│               │
│ - Intersect   │
│ - Generate    │
│ - Ideas       │
└───────────────┘
        │
        ▼
┌───────────────┐
│   Module 4    │
│   Evaluator   │
│               │
│ - Literature  │
│ - Scoring    │
│ - Scoring     │
└───────────────┘
        │
        ▼
┌───────────────┐
│   Module 5    │
│   Reporter    │
│               │
│ - Markdown    │
│ - Reports     │
│ - Export      │
└───────────────┘
```

## Component Details

### Module 1: Harvester
- **Purpose**: Fetch papers from arxiv
- **Input**: Domain configuration, custom queries
- **Output**: List of Paper objects
- **Key Features**:
  - Domain-specific category filtering
  - Date filtering (2024+)
  - Deduplication by arxiv_id
  - Configurable query sets

### Module 2: Autopsy
- **Purpose**: Extract limitations from papers
- **Input**: Paper objects with PDF URLs
- **Output**: PaperAnalysis objects
- **Key Features**:
  - PDF parsing with PyMuPDF
  - LLM-based extraction
  - Focus on Discussion/Conclusion sections
  - Structured output (limitations, future work, vulnerabilities)

### Module 3: Synthesizer
- **Purpose**: Generate novel research ideas
- **Input**: List of PaperAnalysis objects
- **Output**: ResearchIdea object
- **Key Features**:
  - Intersection of limitations
  - Non-incremental idea generation
  - ICML-style output format
  - Cross-disciplinary bridging

### Module 4: Evaluator
- **Purpose**: Evaluate research ideas
- **Input**: ResearchIdea object
- **Output**: Evaluation object
- **Key Features**:
  - Multi-source literature search
  - 7-point scoring rubric
  - Detailed feedback generation
  - De-risking experiments

### Module 5: Reporter
- **Purpose**: Generate markdown reports
- **Input**: ResearchIdea + Evaluation
- **Output**: Markdown file
- **Key Features**:
  - Comprehensive report format
  - Template-based generation
  - Timestamped filenames

## Data Flow

```
User Input (Domain, Provider, Model)
    │
    ▼
Configuration → Harvester
    │
    ▼
Papers → Autopsy → PaperAnalyses
    │
    ▼
PaperAnalyses → Synthesizer → ResearchIdea
    │
    ▼
ResearchIdea → Evaluator → Evaluation
    │
    ▼
ResearchIdea + Evaluation → Reporter → Markdown Report
```

## LLM Provider Architecture

```
LLMProvider (Factory)
    │
    ├── Google Gemini
    │   └── ChatGoogleGenerativeAI
    │
    ├── Anthropic Claude
    │   └── ChatAnthropic
    │
    ├── OpenAI
    │   └── ChatOpenAI
    │
    ├── OpenRouter
    │   └── ChatOpenAI (custom base_url)
    │
    ├── Groq
    │   └── ChatOpenAI (custom base_url)
    │
    └── Together AI
        └── ChatOpenAI (custom base_url)
```

## Literature Search Architecture

```
LiteratureSearcher
    │
    ├── arXiv Search (direct API)
    ├── Google Scholar (via SerpAPI)
    ├── Semantic Scholar (via API)
    └── OpenReview (via web search)
    │
    ▼
Formatted Results → Evaluator
```

## Evaluation Framework Flow

```
Step 0: Literature Quick-Scan
    ├── Search multiple sources
    ├── Format results
    └── Prefer recent papers
    │
Step 1: Scoring Rubric
    ├── Novelty (0-2)
    ├── Audacity (0-2)
    ├── Feasibility (0-2)
    └── Cross-Disciplinary (0-1)
    │
Step 2: Total Score (0-7)
    │
Step 3: Feedback Generation
    ├── Overall summary
    ├── Feedback table
    └── Thinking prompts
    │
Step 4: De-Risking
    ├── Unanswered questions
    └── Concrete experiments
```

