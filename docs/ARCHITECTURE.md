# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Autonomous Research Scientist                │
│                         (Sensei)                                 │
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
│   (Judge)     │
│               │
│ - Literature  │
│ - Scoring     │
│ - Feedback    │
└───────────────┘
        │
        ├─→ Pass? ──┐
        │           │
        └─→ Fail?   │
                    │
        ┌───────────┘
        │
        ▼
┌───────────────┐
│   Module 4b   │
│   Refiner     │
│               │
│ - Improve     │
│ - Address     │
│ - Refine      │
└───────────────┘
        │
        └─── Loop back to Evaluator (up to 2 iterations)
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
        │
        ├─→ Passed Threshold? ──┐
        │                        │
        └─→ No ──────────────────┘
        │
        ▼
┌───────────────┐
│   Module 6    │
│ Code Generator│
│               │
│ - Model Code  │
│ - Training    │
│ - Experiments │
│ - Benchmarks  │
│ - Ablations   │
│ - Configs     │
└───────────────┘
```

## Component Details

### Module 1: Harvester
- **Purpose**: Fetch papers from arxiv
- **Input**: Domain configuration, custom queries, or natural language description
- **Output**: List of Paper objects
- **Key Features**:
  - Domain-specific category filtering (21+ pre-configured domains)
  - Date filtering (2024+)
  - Deduplication by arxiv_id
  - Configurable query sets
  - Natural language query generation: users can describe research interests in natural language, and the system generates search queries automatically

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
  - Conference-style output format
  - Cross-disciplinary bridging

### Module 4: Evaluator (Judge)
- **Purpose**: Evaluate research ideas and provide detailed feedback
- **Input**: ResearchIdea object
- **Output**: Evaluation object with scores and feedback
- **Key Features**:
  - Multi-source literature search
  - 7-point scoring rubric
  - Detailed feedback generation
  - De-risking experiments
  - Actionable weakness identification

### Module 4b: Refiner
- **Purpose**: Iteratively improve ideas based on judge feedback
- **Input**: ResearchIdea + Evaluation feedback
- **Output**: Refined ResearchIdea object
- **Key Features**:
  - Addresses specific weaknesses identified by judge
  - Preserves strengths of original idea
  - Makes concrete improvements
  - Focuses on feasibility, novelty, audacity improvements
  - Part of "Agents as a Loop and Judge" mechanism

### Module 5: Reporter
- **Purpose**: Generate markdown reports
- **Input**: ResearchIdea + Evaluation
- **Output**: Markdown file
- **Key Features**:
  - Comprehensive report format
  - Template-based generation
  - Timestamped filenames

### Module 6: Code Generator
- **Purpose**: Generate complete research project code for approved ideas
- **Input**: ResearchIdea + Evaluation (only if passed threshold)
- **Output**: Complete project directory with all code files
- **Key Features**:
  - Generates model/architecture code
  - Creates training and evaluation scripts
  - Includes experiment infrastructure
  - Generates benchmark and ablation code
  - Creates configuration files
  - Produces documentation (README, setup instructions)
  - Generates requirements.txt
  - All code is production-ready and runnable

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
PaperAnalyses → Synthesizer → ResearchIdea (Initial)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│         Agents as a Loop and Judge Mechanism          │
│                                                       │
│  ResearchIdea → Evaluator (Judge) → Evaluation        │
│       │                    │                          │
│       │                    ├─→ Pass? → Done        │
│       │                    │                          │
│       │                    └─→ Fail? → Continue      │
│       │                                              │
│       └─── Evaluation → Refiner → Refined Idea ────┘
│                           │                          │
│                           └─── Loop (max 2x) ────────┘
│                                                       │
└─────────────────────────────────────────────────────┘
    │
    ▼
ResearchIdea (Best) + Evaluation → Reporter → Markdown Report
    │
    ├─→ Passed Threshold? ──→ Code Generator → Complete Project Code
    │
    └─→ Not Passed ──→ End
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

