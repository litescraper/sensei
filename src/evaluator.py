"""
Module 4: The Evaluator - The Critic

Implements the exact evaluation protocol from the template:
- Step 0: Literature quick-scan (grounding)
- Step 1: Score the idea with rubric
- Step 2: Total score
- Step 3: Overall summary and Feedback
- Step 4: Unanswered Questions and De-risking experiments
"""
import os
from typing import Optional
import logging
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .literature_searcher import LiteratureSearcher
from .models import ResearchIdea, Evaluation
from .llm_providers import LLMProvider

logger = logging.getLogger(__name__)


class Evaluator:
    """Validates research ideas using a comprehensive evaluation framework."""
    
    # Minimum score threshold to pass
    MIN_PASSING_SCORE = 5
    
    def __init__(
        self,
        provider: str = "google",
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        serpapi_key: Optional[str] = None,
        semanticscholar_key: Optional[str] = None
    ):
        """
        Initialize the Evaluator.
        
        Args:
            provider: LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
            model_name: Specific model name (defaults to provider's best model)
            temperature: Temperature for LLM generation (default: 0.1 for strict evaluation)
            serpapi_key: SerpAPI key for Google Search
            semanticscholar_key: Semantic Scholar API key
        """
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        # Initialize literature searcher
        self.literature_searcher = LiteratureSearcher(
            serpapi_key=serpapi_key or os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=semanticscholar_key or os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        # Initialize output parser
        self.evaluation_parser = PydanticOutputParser(pydantic_object=Evaluation)
        
        # Build the evaluation prompt matching the EXACT template format
        system_template = """You are a hard-to-please expert evaluator who LOVES audacious, high-novelty, yet feasible AI research ideas.

Your job is to stress-test a raw idea, then outline what to try next.

You will evaluate research ideas using the following protocol:

–––––––––
EVALUATION PROTOCOL
–––––––––

Step 0 Literature quick-scan (grounding)
You have been provided with a list of papers closest to the idea from multiple sources (arXiv, Google Scholar, Semantic Scholar, OpenReview). Each paper is listed as "[PaperID] Title – why it matters (≤ 15 words)".

**Prefer recent papers over old papers** when making your assessment.

Step 1 Score the idea with the rubric below

**Novelty**
- Give 1 point if you found only a few or no papers related to the idea
- Give 1 point if you notice substantially new framing, hypothesis, or method unseen in key papers
- Deduct 1 point if you found many papers related to the idea

**Audacity**
- Give 2 points if the idea is so audacious that it's worthy of mainstream news (if successful)
- Give 1 point if the idea (if successful) will make scientists take notice and say: "I didn't realize this was possible"
- Deduct 1 point if the idea is incremental, and something that seems to be done just to get a paper

**Feasibility and Risk**
- Give 1 point if the idea is achievable with today's data, compute, methods and tooling (be reasonable - standard GPU clusters and public datasets are acceptable)
- Give 1 point if first steps and intermediate milestones are clear (even if partially described)
- Deduct 1 point ONLY if there are severe hidden blockers that make the idea fundamentally unfeasible (e.g., requires data that doesn't exist, needs quantum computers, violates physical laws)
- Be fair: If an idea requires standard research infrastructure (GPUs, public datasets, existing tooling), it should get feasibility points. Only penalize if it requires unrealistic resources or has fundamental technical barriers.

**Others**
- Give 1 point if research idea is cross-disciplinary in nature (bridging distant fields like physics and computer science)

Step 2 Total score (out of 7 maximum points)

Step 3 Overall summary and Feedback

Give detailed feedback to the person who generated the idea explaining your rationale. Your feedback must be helpful in a way that helps this person think about whether their idea is novel, audacious and feasible. 

You MUST provide a feedback table with the following columns:
- Weakness: Main weakness of the idea
- Thinking Prompt (Novelty): Specific thinking prompt with example on how to be significantly more novel
- Thinking Prompt (Audacity): Specific thinking prompt with example on how to be significantly more audacious
- Thinking Prompt (Feasibility): Specific thinking prompt with example on how to be significantly more feasible
- Why Important: Explanation of WHY it's important to be novel, audacious, and feasible

You should make the person think deeply, so also explain WHY it's important to be novel, audacious and feasible.

Step 4 Unanswered Questions and De-risking experiments

Suggest key unanswered questions and a few initial **concrete experiments** or analyses that de-risk the idea. Each experiment should be specific and actionable.

Be strict but fair. Evaluate ideas rigorously, but:
- Don't be overly harsh on feasibility - standard research infrastructure (GPUs, public datasets) is acceptable
- Reward ideas that have clear validation paths, even if they require some engineering effort
- Most good ideas should score 4-5/7. Exceptional ideas score 6-7/7. Only truly weak ideas should score below 4/7.
- Remember: The goal is to identify promising research directions, not to reject everything

Output your evaluation as a JSON object matching the Evaluation schema."""
        
        human_template = """–––––––––
INPUT
–––––––––

<YOUR RESEARCH IDEA>

Title: {idea_title}
Abstract: {idea_abstract}
Introduction: {idea_introduction}
Method: {idea_method}
Expected Results: {idea_expected_results}
Keywords: {idea_keywords}

–––––––––
LITERATURE QUICK-SCAN RESULTS
–––––––––

{literature_results}

{format_instructions}"""
        
        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def evaluate(self, idea: ResearchIdea) -> Evaluation:
        """
        Evaluate a research idea using the evaluation framework.
        
        Implements the complete evaluation protocol:
        - Step 0: Literature quick-scan
        - Step 1: Scoring with rubric
        - Step 2: Total score
        - Step 3: Overall summary and feedback
        - Step 4: Unanswered questions and de-risking experiments
        
        Args:
            idea: ResearchIdea to evaluate
        
        Returns:
            Evaluation object
        """
        try:
            # Step 0: Literature quick-scan (grounding)
            logger.info("Step 0: Performing literature quick-scan...")
            papers, formatted_literature = self.literature_searcher.comprehensive_search(
                idea_title=idea.title,
                idea_keywords=idea.keywords,
                max_results_per_source=10
            )
            
            logger.info(f"Found {len(papers)} papers in literature search")
            
            # Step 1-4: LLM evaluation
            logger.info("Steps 1-4: Evaluating idea with LLM...")
            
            format_instructions = self.evaluation_parser.get_format_instructions()
            
            messages = self.prompt.format_messages(
                idea_title=idea.title,
                idea_abstract=idea.abstract,
                idea_introduction=idea.introduction,
                idea_method=idea.method,
                idea_expected_results=idea.expected_results,
                idea_keywords=", ".join(idea.keywords),
                literature_results=formatted_literature or "No papers found in literature search.",
                format_instructions=format_instructions
            )
            
            # Call LLM for evaluation
            response = self.llm.invoke(messages)
            
            # Parse response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            
            # Try to find JSON object in content
            import json
            import re
            
            # First, try to extract JSON object if it's embedded in text
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)
            
            # Pre-sanitize content: replace em dashes and other problematic characters
            # This fixes common JSON parsing issues before attempting to parse
            content = content.replace("–", "-").replace("—", "-")  # Replace em/en dashes with regular dash
            
            # Sanitize the content - escape special characters in strings
            # This is a workaround for JSON with special characters
            try:
                # Try parsing as-is first
                evaluation = self.evaluation_parser.parse(content)
            except Exception as parse_error:
                logger.warning(f"Initial parse failed, attempting to fix JSON: {parse_error}")
                
                # Try to fix common JSON issues
                try:
                    # Replace problematic characters in string values
                    # Fix em dashes and other special characters
                    fixed_content = content
                    
                    # Escape unescaped quotes within string values
                    # This is tricky, so we'll try a different approach
                    # Parse as JSON and fix the literature_papers field
                    json_obj = json.loads(content)
                    
                    # Sanitize literature_papers if it exists
                    if "literature_papers" in json_obj and isinstance(json_obj["literature_papers"], list):
                        json_obj["literature_papers"] = [
                            str(paper).replace("\n", " ").replace("\r", " ")
                            .replace("–", "-").replace("—", "-")  # Replace em/en dashes
                            .replace('"', "'")  # Replace problematic quotes
                            for paper in json_obj["literature_papers"]
                        ]
                    
                    # Re-serialize and parse
                    fixed_json_str = json.dumps(json_obj, ensure_ascii=False)
                    evaluation = self.evaluation_parser.parse(fixed_json_str)
                    logger.info("Successfully fixed and parsed JSON")
                    
                except Exception as fix_error:
                    logger.error(f"Failed to fix JSON: {fix_error}")
                    logger.error(f"Response content (first 1000 chars): {content[:1000]}...")
                    
                    # Last resort: try to manually construct a minimal valid evaluation
                    try:
                        # Extract what we can from the malformed JSON
                        score_match = re.search(r'"total_score":\s*(\d+)', content)
                        novelty_match = re.search(r'"novelty_score":\s*(\d+)', content)
                        audacity_match = re.search(r'"audacity_score":\s*(\d+)', content)
                        feasibility_match = re.search(r'"feasibility_score":\s*(\d+)', content)
                        cross_match = re.search(r'"cross_disciplinary_score":\s*(\d+)', content)
                        
                        total_score = int(score_match.group(1)) if score_match else 0
                        novelty_score = int(novelty_match.group(1)) if novelty_match else 0
                        audacity_score = int(audacity_match.group(1)) if audacity_match else 0
                        feasibility_score = int(feasibility_match.group(1)) if feasibility_match else 0
                        cross_score = int(cross_match.group(1)) if cross_match else 0
                        
                        # Extract justifications if possible (simplified extraction)
                        novelty_just = "Extracted from evaluation" 
                        audacity_just = "Extracted from evaluation"
                        feasibility_just = "Extracted from evaluation"
                        cross_just = "Extracted from evaluation"
                        
                        # Create a minimal valid evaluation
                        from .models import Score, Evaluation, ValidationFeedback
                        
                        score = Score(
                            novelty_score=novelty_score,
                            audacity_score=audacity_score,
                            feasibility_score=feasibility_score,
                            cross_disciplinary_score=cross_score,
                            total_score=total_score,
                            novelty_justification=novelty_just,
                            audacity_justification=audacity_just,
                            feasibility_justification=feasibility_just,
                            cross_disciplinary_justification=cross_just
                        )
                        
                        evaluation = Evaluation(
                            score=score,
                            literature_papers=[],
                            literature_summary="JSON parsing failed, using fallback",
                            overall_summary="Evaluation completed but JSON parsing encountered errors. Please review the raw output.",
                            feedback_table=[ValidationFeedback(
                                weakness="JSON parsing error occurred",
                                thinking_prompt_novelty="Review the evaluation output manually",
                                thinking_prompt_audacity="Review the evaluation output manually",
                                thinking_prompt_feasibility="Review the evaluation output manually",
                                why_important="Manual review needed due to parsing error"
                            )],
                            unanswered_questions=["JSON parsing error - manual review required"],
                            de_risking_experiments=["Review the evaluation output manually"],
                            passed_threshold=total_score >= self.MIN_PASSING_SCORE
                        )
                        
                        logger.warning("Created fallback evaluation due to JSON parsing error")
                        
                    except Exception as fallback_error:
                        logger.error(f"Fallback evaluation creation failed: {fallback_error}")
                        raise ValueError(f"Failed to parse LLM evaluation response after all attempts: {parse_error}")
            
            evaluation.literature_papers = formatted_literature.split("\n") if formatted_literature else []
            evaluation.literature_summary = f"Found {len(papers)} papers across multiple sources. Preferring recent papers."
            evaluation.passed_threshold = evaluation.score.total_score >= self.MIN_PASSING_SCORE
            
            logger.info(f"Evaluation complete. Score: {evaluation.score.total_score}/7")
            logger.info(f"Passed threshold: {evaluation.passed_threshold}")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating idea: {e}")
            raise

