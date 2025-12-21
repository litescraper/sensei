from typing import List, Optional
import logging
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .models import PaperAnalysis, ResearchIdea
from .llm_providers import LLMProvider

logger = logging.getLogger(__name__)


class Synthesizer:
    """Generates novel research ideas by intersecting limitations from multiple papers."""
    
    def __init__(
        self,
        provider: str = "google",
        model_name: Optional[str] = None,
        temperature: float = 0.8,
        target_conference: Optional[str] = None
    ):
        self.target_conference = target_conference
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        # Initialize output parser
        self.output_parser = PydanticOutputParser(pydantic_object=ResearchIdea)
        
        # Store feedback from previous attempts
        self.last_feedback = None
        
        # Build the enhanced Inventor prompt
        conference_context = ""
        if self.target_conference and self.target_conference != "General (No specific conference target)":
            conference_context = f"""
TARGET CONFERENCE: {self.target_conference}

You are generating a research idea specifically targeting {self.target_conference}. Consider:
- The typical scope, style, and expectations of {self.target_conference}
- Recent trends and accepted papers at {self.target_conference}
- The level of rigor, novelty, and impact expected for {self.target_conference}
- Methodological preferences and evaluation standards common at {self.target_conference}
- The type of contributions that are most valued at {self.target_conference}

Your idea should be tailored to fit {self.target_conference}'s standards and expectations while maintaining high quality and novelty.

"""
        
        system_template = f"""You are a Senior Research Scientist specializing in generating groundbreaking research ideas by deeply understanding existing work and proposing novel solutions.
{conference_context}
Your mission is to generate research ideas that:
1. Understand what each paper does (their methods, techniques, contributions)
2. Identify their strengths and how they can be leveraged
3. Recognize their limitations and vulnerabilities
4. Propose novel solutions that combine the best of multiple approaches

Constraints:
1. DO NOT propose incremental improvements. Examples of what NOT to propose:
   - "Fine-tune on more data"
   - "Use a larger model"
   - "Add more layers"
   - "Improve the loss function slightly"
   - "Try different hyperparameters"

2. DO propose mechanisms that:
   - Combine strengths from Paper A with solutions to limitations from Paper B
   - Use techniques from one paper to address problems in another
   - Bridge distant fields (e.g., Control Theory + AI Safety, Game Theory + Adversarial ML)
   - Implement the suggested improvements in novel ways
   - Apply potential solutions in creative combinations
   - Introduce fundamentally new framing or hypotheses

3. Your ideas should be:
   - Novel: Few or no existing papers should address this exact problem in this way
   - Audacious: Worthy of mainstream news coverage
   - Feasible: Must be achievable with today's compute and data resources. Prioritize:
     * Ideas that can be validated with existing datasets or easy-to-collect data
     * Methods that don't require massive compute (prefer approaches that work with standard GPUs)
     * Clear, simple first steps and intermediate milestones
     * Avoid requiring multiple complex subsystems that need tight integration
     * Prefer incremental validation paths (can test components independently)
   - Cross-disciplinary: When possible, bridge AI with other fields
   - Solution-oriented: Directly address identified limitations with concrete approaches

FEASIBILITY GUIDELINES:
- Start simple: Propose ideas that can be validated with a minimal viable experiment
- Use existing resources: Leverage available datasets, pretrained models, and standard tooling
- Clear milestones: Break down the idea into testable components
- Avoid over-engineering: Don't combine too many complex subsystems unless absolutely necessary
- Practical validation: Ensure the idea can be evaluated without requiring massive infrastructure

TASK:
You have access to comprehensive analyses of recent papers. Each analysis includes:
- What the paper does (contribution, methodology, techniques)
- Strengths of the approach
- Limitations and vulnerabilities
- Suggested improvements and potential solutions

Your job is to:
1. Understand the methods and techniques from each paper
2. Identify how strengths from one paper could address limitations in another
3. Combine suggested improvements in novel ways
4. Propose solutions that leverage the best techniques while solving real problems

Generate a research idea that:
- Has a clear, compelling title
- Includes a structured abstract (150-200 words)
- Provides an introduction explaining the problem and why it matters
- Describes a concrete method/approach that combines techniques from multiple papers
- Explains how it addresses specific limitations using identified solutions
- Outlines expected results and how they would be evaluated
- Includes 5-10 keywords for literature search validation
- Explicitly describes:
  * What datasets/resources are needed (prefer existing/public datasets)
  * What compute requirements are expected (be realistic)
  * What are the first steps and intermediate milestones
  * How each component can be validated independently
  * What is the minimal viable experiment to test the core hypothesis

Output your idea as a JSON object matching the ResearchIdea schema."""
        
        human_template = """Comprehensive Paper Analyses:

{knowledge_context}

{failure_feedback}

Based on the above analyses, generate a novel research idea that:
1. Understands what each paper does and their key techniques
2. Leverages their strengths
3. Addresses their limitations using suggested improvements and potential solutions
4. Combines methods in novel ways to create something greater than the sum of parts
{failure_instructions}

{format_instructions}"""
        
        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def _flatten_analyses(self, analyses: List[PaperAnalysis]) -> str:
        context_parts = []
        
        for i, analysis in enumerate(analyses, 1):
            context_parts.append(f"\n{'='*60}")
            context_parts.append(f"Paper {i}: {analysis.paper_title}")
            context_parts.append(f"{'='*60}\n")
            
            # What the paper does
            context_parts.append("MAIN CONTRIBUTION:")
            context_parts.append(f"  {analysis.main_contribution}")
            context_parts.append("")
            
            context_parts.append("METHODOLOGY:")
            context_parts.append(f"  {analysis.methodology}")
            context_parts.append("")
            
            if analysis.key_techniques:
                context_parts.append("KEY TECHNIQUES:")
                for technique in analysis.key_techniques:
                    context_parts.append(f"  - {technique}")
                context_parts.append("")
            
            # Strengths
            if analysis.strengths:
                context_parts.append("STRENGTHS:")
                for strength in analysis.strengths:
                    context_parts.append(f"  - {strength}")
                context_parts.append("")
            
            # Limitations
            if analysis.limitations:
                context_parts.append("EXPLICIT LIMITATIONS:")
                for lim in analysis.limitations:
                    context_parts.append(f"  - {lim}")
                context_parts.append("")
            
            if analysis.future_work:
                context_parts.append("UNSOLVED PROBLEMS (Future Work):")
                for fw in analysis.future_work:
                    context_parts.append(f"  - {fw}")
                context_parts.append("")
            
            if analysis.vulnerabilities:
                context_parts.append("BRITTLENESS/VULNERABILITIES:")
                for vuln in analysis.vulnerabilities:
                    context_parts.append(f"  - {vuln}")
                context_parts.append("")
            
            # Solutions and improvements
            if analysis.suggested_improvements:
                context_parts.append("SUGGESTED IMPROVEMENTS:")
                for improvement in analysis.suggested_improvements:
                    context_parts.append(f"  - {improvement}")
                context_parts.append("")
            
            if analysis.potential_solutions:
                context_parts.append("POTENTIAL SOLUTIONS:")
                for solution in analysis.potential_solutions:
                    context_parts.append(f"  - {solution}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def generate_idea(self, analyses: List[PaperAnalysis]) -> ResearchIdea:
        try:
            # Flatten analyses into knowledge context
            knowledge_context = self._flatten_analyses(analyses)
            
            logger.info(f"Generating research idea from {len(analyses)} paper analyses")
            
            # Format prompt
            format_instructions = self.output_parser.get_format_instructions()
            
            # Add feedback from previous attempts if available
            failure_feedback = ""
            failure_instructions = ""
            if self.last_feedback:
                failure_feedback = f"""
PREVIOUS ATTEMPT FEEDBACK:
The previous idea scored {self.last_feedback['total_score']}/7 and failed feasibility evaluation.
Feasibility Score: {self.last_feedback['feasibility_score']}/2
Feedback: {self.last_feedback['feasibility_justification']}

For this attempt, focus heavily on feasibility:
- Simplify the approach - avoid complex multi-component systems
- Use existing datasets and standard compute resources
- Provide clear, simple validation steps
- Break down into independently testable components
"""
                failure_instructions = "\n5. Prioritize feasibility - make the idea simpler and more practical than the previous attempt"
            
            messages = self.prompt.format_messages(
                knowledge_context=knowledge_context,
                format_instructions=format_instructions,
                failure_feedback=failure_feedback,
                failure_instructions=failure_instructions
            )
            
            # Call LLM
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
            
            try:
                idea = self.output_parser.parse(content)
            except Exception as parse_error:
                logger.error(f"Failed to parse idea response: {parse_error}")
                logger.error(f"Response content: {content[:500]}...")
                raise ValueError(f"Failed to parse LLM idea response: {parse_error}")
            
            logger.info(f"Generated research idea: {idea.title}")
            return idea
            
        except Exception as e:
            logger.error(f"Error generating research idea: {e}")
            raise

