"""
Refinement Agent - Refines ideas based on judge feedback.

Part of the "Agents as a Loop and Judge" mechanism where:
1. Generator creates initial idea
2. Judge evaluates and provides feedback
3. Refiner improves the idea based on feedback
4. Loop continues until idea passes or max iterations
"""
from typing import Optional
import logging
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .models import ResearchIdea, Evaluation
from .llm_providers import LLMProvider

logger = logging.getLogger(__name__)


class Refiner:
    """Refines research ideas based on evaluation feedback."""
    
    def __init__(
        self,
        provider: str = "google",
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the Refiner.
        
        Args:
            provider: LLM provider
            model_name: Model name
            temperature: Temperature for refinement (default: 0.7 for balanced creativity)
        """
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=ResearchIdea)
        
        system_template = """You are an expert research idea refiner. Improve research ideas based on evaluation feedback.

Your task is to take an existing research idea and refine it to address specific weaknesses and improve scores across novelty, audacity, feasibility, and cross-disciplinary impact.

Principles:
1. Address specific weaknesses identified by the judge
2. Preserve strengths of the original idea
3. Make concrete, actionable improvements
4. Improve feasibility by simplifying approach, using existing resources, clarifying milestones
5. Enhance novelty by introducing new framing, combining techniques, bridging fields
6. Increase audacity while maintaining feasibility

Strategy:
- Read evaluation feedback carefully
- Identify main weaknesses from feedback table
- Propose concrete improvements for each weakness
- Revise idea components (title, abstract, method) to incorporate improvements
- Ensure refined idea is better while maintaining coherence

Output the refined idea as a JSON object matching the ResearchIdea schema."""
        
        human_template = """ORIGINAL IDEA:

Title: {original_title}
Abstract: {original_abstract}
Introduction: {original_introduction}
Method: {original_method}
Expected Results: {original_expected_results}
Keywords: {original_keywords}

EVALUATION FEEDBACK:

Total Score: {total_score}/7
Passed Threshold: {passed_threshold}

Score Breakdown:
- Novelty: {novelty_score}/2 - {novelty_justification}
- Audacity: {audacity_score}/2 - {audacity_justification}
- Feasibility: {feasibility_score}/2 - {feasibility_justification}
- Cross-Disciplinary: {cross_disciplinary_score}/1 - {cross_disciplinary_justification}

Overall Summary:
{overall_summary}

Key Weaknesses Identified:
{weaknesses}

Thinking Prompts for Improvement:
{thinking_prompts}

De-risking Experiments Suggested:
{de_risking_experiments}

TASK:
Refine the original idea to address the weaknesses and improve the scores. The refined idea should:
1. Directly address each identified weakness
2. Incorporate suggestions from the thinking prompts
3. Be more feasible, novel, audacious, or cross-disciplinary (depending on what scored low)
4. Maintain coherence and feasibility

Output the REFINED idea as a JSON object matching the ResearchIdea schema.

{format_instructions}"""
        
        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def refine_idea(self, idea: ResearchIdea, evaluation: Evaluation) -> ResearchIdea:
        """
        Refine an idea based on evaluation feedback.
        
        Args:
            idea: Original ResearchIdea
            evaluation: Evaluation feedback from judge
            
        Returns:
            Refined ResearchIdea
        """
        try:
            logger.info("Refining idea based on evaluation feedback...")
            
            # Extract weaknesses from feedback table
            weaknesses = []
            thinking_prompts = []
            for feedback in evaluation.feedback_table:
                weaknesses.append(f"- {feedback.weakness}")
                thinking_prompts.append(f"Novelty: {feedback.thinking_prompt_novelty}")
                thinking_prompts.append(f"Audacity: {feedback.thinking_prompt_audacity}")
                thinking_prompts.append(f"Feasibility: {feedback.thinking_prompt_feasibility}")
            
            weaknesses_text = "\n".join(weaknesses) if weaknesses else "No specific weaknesses identified."
            thinking_prompts_text = "\n".join(thinking_prompts) if thinking_prompts else "No specific prompts provided."
            de_risking_text = "\n".join([f"- {exp}" for exp in evaluation.de_risking_experiments]) if evaluation.de_risking_experiments else "No experiments suggested."
            
            format_instructions = self.output_parser.get_format_instructions()
            
            messages = self.prompt.format_messages(
                original_title=idea.title,
                original_abstract=idea.abstract,
                original_introduction=idea.introduction,
                original_method=idea.method,
                original_expected_results=idea.expected_results,
                original_keywords=", ".join(idea.keywords),
                total_score=evaluation.score.total_score,
                passed_threshold=evaluation.passed_threshold,
                novelty_score=evaluation.score.novelty_score,
                novelty_justification=evaluation.score.novelty_justification,
                audacity_score=evaluation.score.audacity_score,
                audacity_justification=evaluation.score.audacity_justification,
                feasibility_score=evaluation.score.feasibility_score,
                feasibility_justification=evaluation.score.feasibility_justification,
                cross_disciplinary_score=evaluation.score.cross_disciplinary_score,
                cross_disciplinary_justification=evaluation.score.cross_disciplinary_justification,
                overall_summary=evaluation.overall_summary,
                weaknesses=weaknesses_text,
                thinking_prompts=thinking_prompts_text,
                de_risking_experiments=de_risking_text,
                format_instructions=format_instructions
            )
            
            # Call LLM
            response = self.llm.invoke(messages)
            
            # Parse response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Extract JSON if wrapped in code blocks
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
            
            try:
                refined_idea = self.output_parser.parse(content)
                logger.info(f"Refined idea: {refined_idea.title}")
                return refined_idea
            except Exception as parse_error:
                logger.error(f"Failed to parse refined idea: {parse_error}")
                logger.error(f"Response content: {content[:500]}...")
                raise ValueError(f"Failed to parse LLM refinement response: {parse_error}")
                
        except Exception as e:
            logger.error(f"Error refining idea: {e}")
            raise

