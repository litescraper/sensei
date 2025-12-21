# How It Works

## Overview

The Autonomous Research Scientist is a six-stage pipeline that transforms raw research papers into evaluated, novel research ideas. This document explains the mechanics of each stage.

## Stage 1: Harvesting Papers

### Process

1. **Domain Configuration**: Based on selected domain, the system loads:
   - Domain-specific arxiv categories (e.g., `cs.CR`, `cs.LG` for AI Safety)
   - Domain-specific search queries (e.g., "LLM jailbreak attack defense")

2. **Query Execution**: For each query:
   - Constructs arxiv search with category filters
   - Searches with date sorting (newest first)
   - Retrieves up to `max_results_per_query` papers

3. **Filtering**:
   - **Date Filter**: Only papers published after 2024-01-01
   - **Category Filter**: Only papers in domain-specific categories
   - **Deduplication**: Removes duplicates by arxiv_id

4. **Output**: List of `Paper` objects with:
   - Title, abstract, PDF URL
   - Publication date, authors, categories
   - Arxiv ID for tracking

### Example

```
Query: "LLM jailbreak attack defense"
Categories: cs.CR, cs.LG, cs.CL
Result: 20 papers (after filtering)
```

## Stage 2: Extracting Limitations (Autopsy)

### Process

1. **PDF Download**: 
   - Downloads PDF from arxiv URL
   - Handles 403 errors gracefully
   - Uses PyMuPDF for parsing

2. **Text Extraction**:
   - Extracts full text from all pages
   - Truncates to last 3000 tokens (focuses on Discussion/Conclusion)
   - Preserves structure where possible

3. **LLM Analysis**:
   - Sends paper text to LLM with extraction prompt
   - Prompt specifically targets:
     - **Explicit Limitations**: Where authors admit failure
     - **Unsolved Problems**: Gaps in Future Work
     - **Brittleness**: Hyperparameter sensitivity, fragility

4. **Structured Output**:
   - Parses LLM response as JSON
   - Validates against `PaperAnalysis` schema
   - Returns structured limitations

### Example Output

```json
{
  "limitations": [
    "Method fails on long context inputs (>4096 tokens)",
    "Requires high VRAM (40GB+)"
  ],
  "future_work": [
    "Scale to larger models",
    "Handle multi-modal inputs"
  ],
  "vulnerabilities": [
    "Highly sensitive to learning rate",
    "Fails with adversarial perturbations >0.1 epsilon"
  ]
}
```

## Stage 3: Synthesizing Ideas

### Process

1. **Knowledge Context Building**:
   - Flattens all `PaperAnalysis` objects into a structured string
   - Groups by paper, then by category (limitations, future work, vulnerabilities)
   - Creates "Knowledge Context" for LLM

2. **Idea Generation**:
   - Uses higher temperature (0.8) for creativity
   - Prompt emphasizes:
     - Non-incremental solutions
     - Cross-disciplinary bridging
     - Solving limitations from Paper A using techniques from Paper B
   - Generates structured abstract

3. **Output Structure**:
   - Title
   - Abstract (150-200 words)
   - Introduction
   - Method
   - Expected Results
   - Keywords (for literature search)

### Example

**Input**: Limitations from 2 papers on adversarial RL and circuit discovery

**Output**: "Neuro-Symbolic Adversarial Mechanistic Credit Assignment (NAM-CA): Eliminating Reward Hacking via Circuit-Level Supervision"

## Stage 4: Evaluating Ideas (Agents as a Loop and Judge)

The evaluation stage implements an iterative refinement mechanism where a **Judge** (Evaluator) evaluates ideas and a **Refiner** improves them based on feedback. This loop continues until the idea passes the evaluation threshold or maximum iterations are reached.

### The Judge-Refine Loop

```
1. Generator creates initial idea
   │
   ▼
2. Judge evaluates idea
   │
   ├─→ Passes threshold? → Done, proceed to reporting
   │
   └─→ Fails threshold? → Continue to refinement
       │
       ▼
3. Refiner improves idea based on judge's feedback
   │
   ▼
4. Judge re-evaluates refined idea
   │
   ├─→ Passes? → Done
   │
   └─→ Still fails? → Refine again (up to 2 iterations)
```

### Step 0: Literature Quick-Scan

1. **Multi-Source Search**:
   - **arXiv**: Direct API search
   - **Google Scholar**: Via SerpAPI
   - **Semantic Scholar**: Via official API
   - **OpenReview**: Via web search

2. **Result Formatting**:
   - Formats as "[PaperID] Title – why it matters (≤ 15 words)"
   - Prefers recent papers
   - Deduplicates by title

3. **Output**: List of formatted paper strings

### Step 1: Scoring Rubric

**Novelty (0-2 points)**:
- +1: Few/no related papers found
- +1: Substantially new framing/hypothesis
- -1: Many related papers exist

**Audacity (0-2 points)**:
- +2: Worthy of mainstream news
- +1: "I didn't realize this was possible"
- -1: Incremental engineering

**Feasibility (0-2 points)**:
- +1: Achievable with today's resources
- +1: Clear milestones
- -1: Hidden blockers

**Cross-Disciplinary (0-1 point)**:
- +1: Bridges distant fields

### Step 2: Total Score

Sum of all category scores (0-7 maximum)

### Step 3: Feedback Generation

LLM generates:
- **Overall Summary**: Detailed rationale
- **Feedback Table**: 
  - Weakness
  - Thinking prompts for Novelty, Audacity, Feasibility
  - Why it's important

### Step 4: De-Risking

LLM suggests:
- **Unanswered Questions**: Key unknowns
- **De-Risking Experiments**: Concrete, actionable experiments

### Step 5: Iterative Refinement (Agents as a Loop and Judge)

When an idea fails the evaluation threshold, the **Refiner** agent takes over:

1. **Feedback Analysis**:
   - Extracts weaknesses from evaluation feedback table
   - Identifies low-scoring dimensions (novelty, audacity, feasibility)
   - Reviews thinking prompts for improvement directions

2. **Idea Refinement**:
   - Addresses each identified weakness systematically
   - Preserves strengths of the original idea
   - Makes concrete improvements to method, approach, or framing
   - Focuses on improving the lowest-scoring dimensions

3. **Refinement Strategy**:
   - **Low Novelty**: Introduce new framing, combine techniques in novel ways
   - **Low Audacity**: Increase ambition while maintaining feasibility
   - **Low Feasibility**: Simplify approach, clarify milestones, use existing resources
   - **Low Cross-Disciplinary**: Bridge additional fields or domains

4. **Re-evaluation**:
   - Refined idea goes back to Judge for re-evaluation
   - Process repeats up to 2 refinement iterations
   - Best idea across all iterations is selected

### Benefits of Iterative Refinement

- **Higher Success Rate**: Ideas are improved rather than discarded
- **Targeted Improvements**: Addresses specific weaknesses identified by judge
- **Preserves Good Ideas**: Doesn't throw away promising concepts
- **Systematic Enhancement**: Methodical approach to idea improvement

## Stage 5: Report Generation

### Process

1. **Template Population**:
   - Research idea details
   - Evaluation scores
   - Literature check results
   - Feedback table
   - De-risking experiments

2. **Markdown Formatting**:
   - Structured sections
   - Tables for scores and feedback
   - Code blocks for experiments

3. **File Saving**:
   - Timestamped filename
   - Sanitized title
   - Saved to `reports/` directory

## Error Handling

### Graceful Degradation

- **PDF Download Fails**: Skip paper, continue with others
- **LLM Parsing Fails**: Extract JSON from markdown code blocks
- **API Rate Limits**: Retry with exponential backoff
- **Missing API Keys**: Warn but continue with available services

### Logging

- Comprehensive logging at INFO level
- Warnings for recoverable errors
- Errors for critical failures
- Progress tracking through pipeline

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: Papers can be analyzed in parallel (future enhancement)
2. **Caching**: PDFs and analyses could be cached
3. **Token Limits**: Truncation focuses on most relevant sections
4. **Batch Operations**: Literature search batches queries

### Resource Usage

- **API Calls**: 
  - arXiv: Free, no limits
  - LLM: Depends on provider (rate limits apply)
  - SerpAPI: Paid service, quota-based
  - Semantic Scholar: Free tier available

- **Compute**:
  - PDF parsing: CPU-intensive
  - LLM inference: API-based (no local compute)
  - Literature search: Network I/O

## Extensibility

### Adding New Domains

1. Add domain to `ResearchDomain` enum
2. Add categories to `DOMAIN_CATEGORIES`
3. Add queries to `DOMAIN_QUERIES`

### Adding New LLM Providers

1. Implement provider in `LLMProvider.create_llm()`
2. Add to `AVAILABLE_MODELS` dict
3. Update UI dropdown

### Customizing Evaluation

- Modify `Evaluator` prompts
- Adjust scoring weights
- Add new evaluation criteria

