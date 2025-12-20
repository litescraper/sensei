# Theoretical Foundation

## Core Philosophy: The Evaluation Framework

The evaluation framework is a rigorous protocol designed to identify research ideas that are simultaneously **novel**, **audacious**, and **feasible**. The framework is based on the principle that impactful research must satisfy all three criteria.

### Theoretical Basis

#### 1. Novelty Requirement

**Hypothesis**: Truly impactful research addresses problems that haven't been solved, or solves them in fundamentally new ways.

**Mathematical Formulation**:
```
Novelty(I) = 1 - Similarity(I, Literature)
```

Where `Similarity(I, Literature)` measures semantic overlap with existing work.

**Why It Matters**: 
- Incremental research has diminishing returns
- Novel ideas open new research directions
- High novelty → High citation potential

#### 2. Audacity Requirement

**Hypothesis**: Research that challenges fundamental assumptions or bridges distant fields has higher impact potential.

**Definition**: An idea is "audacious" if:
- It would make experts say "I didn't realize this was possible"
- It's worthy of mainstream news coverage
- It challenges existing paradigms

**Why It Matters**:
- Audacious ideas inspire follow-up work
- They attract top talent
- They define new research areas

#### 3. Feasibility Requirement

**Hypothesis**: Ideas must be achievable with current resources to have near-term impact.

**Constraints**:
- **Data**: Available datasets or synthetic generation methods
- **Compute**: Accessible hardware/cloud resources
- **Methods**: Established techniques or clear extensions
- **Evaluation**: Definable success metrics

**Why It Matters**:
- Unfeasible ideas remain theoretical curiosities
- Feasibility enables rapid iteration
- Achievable milestones build momentum

#### 4. Cross-Disciplinary Bonus

**Hypothesis**: Ideas that bridge distant fields leverage complementary knowledge.

**Mechanism**: 
- Different fields have different problem-solving approaches
- Cross-pollination creates novel solutions
- Reduces risk of being "solved" by single-field experts

## The Intersection Principle

### Core Idea

The Synthesizer module implements the **Intersection Principle**:

> Novel research ideas emerge at the intersection of unsolved problems from different papers.

### Mathematical Model

Given papers P₁, P₂, ..., Pₙ with limitations L₁, L₂, ..., Lₙ:

```
Idea = f(Intersect(L₁, L₂, ..., Lₙ))
```

Where `f` is a creative synthesis function (implemented by LLM).

### Why This Works

1. **Complementary Weaknesses**: Paper A's limitation might be solvable using Paper B's technique
2. **Gap Identification**: Intersections reveal research gaps
3. **Cross-Domain Transfer**: Techniques from one domain solve problems in another

## Literature Grounding Theory

### The Grounding Problem

**Problem**: How do we ensure generated ideas aren't already published?

**Solution**: Multi-source literature search with semantic similarity checking.

### Search Strategy

1. **Breadth**: Search multiple sources (arXiv, Scholar, Semantic Scholar, OpenReview)
2. **Recency**: Prefer recent papers (captures latest work)
3. **Similarity**: Check semantic overlap with generated idea

### Similarity Metric

```
Similarity(Idea, Paper) = |Keywords(Idea) ∩ Keywords(Paper)| / |Keywords(Idea)|
```

If `Similarity > 0.70`, idea is considered too similar.

## Credit Assignment in Research Synthesis

### The Problem

When intersecting limitations from multiple papers, how do we attribute credit?

### Our Approach

1. **Explicit Attribution**: Generated ideas reference source papers
2. **Novel Combination**: Credit goes to the novel intersection, not individual limitations
3. **Transparency**: Reports include literature check results

## Evaluation Rigor

### Why Strict Evaluation?

**Principle**: Most ideas should score 3-4/7. Only exceptional ideas score 5-7/7.

**Rationale**:
- Prevents false positives
- Ensures high-quality output
- Maintains research standards

### Scoring Distribution

```
Score Distribution (Expected):
3-4/7: 60% of ideas (good but not exceptional)
5-6/7: 30% of ideas (strong candidates)
7/7:   10% of ideas (exceptional, rare)
```

### Calibration

The framework is calibrated such that:
- Ideas scoring 5+ are publication-worthy
- Ideas scoring 6+ are top-tier conference material
- Ideas scoring 7 are potentially groundbreaking

## Limitations and Future Work

### Current Limitations

1. **LLM Dependency**: Quality depends on LLM capabilities
2. **Literature Search**: May miss very recent or niche work
3. **Domain Expertise**: System doesn't have deep domain knowledge
4. **Evaluation Subjectivity**: Some aspects of evaluation are inherently subjective

### Theoretical Extensions

1. **Multi-Agent Systems**: Multiple specialized agents for different domains
2. **Active Learning**: System learns from user feedback
3. **Meta-Learning**: System improves idea generation over time
4. **Causal Reasoning**: Explicit causal models for idea validation

## References

- Evaluation Framework: Comprehensive scoring protocol
- Intersection Principle: Inspired by combinatorial creativity theory
- Literature Grounding: Based on information retrieval theory
- Credit Assignment: Draws from reinforcement learning literature

