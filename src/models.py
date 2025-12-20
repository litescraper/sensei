"""
Pydantic models for strict schema validation.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Schema for arxiv paper metadata."""
    title: str
    abstract: str
    pdf_url: str
    published_date: datetime
    arxiv_id: Optional[str] = None
    authors: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    citation_count: Optional[int] = None
    citation_velocity: Optional[float] = None  # citations per month


class PaperAnalysis(BaseModel):
    """Schema for comprehensive paper analysis including methods, strengths, limitations, and solutions."""
    # What the paper does
    main_contribution: str = Field(
        description="The main contribution or what this paper does"
    )
    methodology: str = Field(
        description="The key methodology, approach, or technique used"
    )
    key_techniques: List[str] = Field(
        default_factory=list,
        description="Specific techniques, algorithms, or methods employed"
    )
    
    # Strengths
    strengths: List[str] = Field(
        default_factory=list,
        description="What the paper does well, novel contributions, advantages"
    )
    
    # Limitations (existing)
    limitations: List[str] = Field(
        default_factory=list,
        description="Explicit limitations where authors admit their method fails"
    )
    future_work: List[str] = Field(
        default_factory=list,
        description="Specific gaps mentioned in Future Work sections"
    )
    vulnerabilities: List[str] = Field(
        default_factory=list,
        description="Brittleness mentions, hyperparameter sensitivity, etc."
    )
    
    # Solutions and improvements
    suggested_improvements: List[str] = Field(
        default_factory=list,
        description="Suggested ways to address the limitations or improve the method"
    )
    potential_solutions: List[str] = Field(
        default_factory=list,
        description="Potential solutions or approaches that could address the identified problems"
    )
    
    paper_title: str
    paper_id: Optional[str] = None


class ResearchIdea(BaseModel):
    """Schema for generated research ideas."""
    title: str
    abstract: str
    introduction: str
    method: str
    expected_results: str
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords for literature search validation"
    )


class LossfunkScore(BaseModel):
    """Schema for Lossfunk Framework evaluation scores."""
    novelty_score: int = Field(ge=0, le=2, description="Novelty score (0-2)")
    audacity_score: int = Field(ge=0, le=2, description="Audacity score (0-2)")
    feasibility_score: int = Field(ge=0, le=2, description="Feasibility score (0-2)")
    cross_disciplinary_score: int = Field(ge=0, le=1, description="Cross-disciplinary score (0-1)")
    total_score: int = Field(ge=0, le=7, description="Total score (0-7)")
    novelty_justification: str
    audacity_justification: str
    feasibility_justification: str
    cross_disciplinary_justification: str


class ValidationFeedback(BaseModel):
    """
    Schema for validation feedback and suggestions.
    
    Matches the template requirement for Step 3: Overall summary and Feedback
    with thinking prompts and examples in table format.
    """
    weakness: str = Field(description="Main weakness of the idea")
    thinking_prompt_novelty: str = Field(
        description="Thinking prompt with example on how to be significantly more novel"
    )
    thinking_prompt_audacity: str = Field(
        description="Thinking prompt with example on how to be significantly more audacious"
    )
    thinking_prompt_feasibility: str = Field(
        description="Thinking prompt with example on how to be significantly more feasible"
    )
    why_important: str = Field(
        description="Explanation of WHY it's important to be novel, audacious, and feasible"
    )


class LossfunkEvaluation(BaseModel):
    """
    Complete evaluation result from Lossfunk Validator.
    
    Matches the exact template format:
    - Step 0: Literature quick-scan (grounding)
    - Step 1: Score the idea with rubric
    - Step 2: Total score
    - Step 3: Overall summary and Feedback
    - Step 4: Unanswered Questions and De-risking experiments
    """
    # Step 0: Literature check results
    literature_papers: List[str] = Field(
        default_factory=list,
        description="List of papers found in format: [PaperID] Title – why it matters"
    )
    literature_summary: str = Field(
        default="",
        description="Summary of literature check results"
    )
    
    # Step 1 & 2: Scoring
    score: LossfunkScore
    
    # Step 3: Overall summary and feedback
    overall_summary: str = Field(
        description="Detailed feedback explaining rationale for scores"
    )
    feedback_table: List[ValidationFeedback] = Field(
        description="Table format feedback with thinking prompts and examples"
    )
    
    # Step 4: Unanswered questions and de-risking
    unanswered_questions: List[str] = Field(
        default_factory=list,
        description="Key unanswered questions about the idea"
    )
    de_risking_experiments: List[str] = Field(
        default_factory=list,
        description="Concrete experiments or analyses that de-risk the idea"
    )
    
    # Metadata
    passed_threshold: bool = Field(
        default=False,
        description="Whether the idea passed the minimum threshold (e.g., >=5/7)"
    )

