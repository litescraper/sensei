"""
Main orchestration script for Sensei - Autonomous Research Scientist.

Sensei is an autonomous research system that generates novel research ideas
in AI Safety, Trustworthy AI, Adversarial Machine Learning, and Jailbreaking domains
using a comprehensive evaluation framework.
"""
import os
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

from .harvester import Harvester
from .autopsy import Autopsy
from .synthesizer import Synthesizer
from .evaluator import Evaluator
from .refiner import Refiner
from .reporter import Reporter
from .code_generator import CodeGenerator
from .config import ResearchDomain
from .models import (
    Paper,
    PaperAnalysis,
    ResearchIdea,
    Evaluation,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Sensei:
    """Main orchestration class for the Autonomous Research Scientist."""
    
    def __init__(
        self,
        domain: ResearchDomain = ResearchDomain.AI_SAFETY,
        custom_queries: Optional[List[str]] = None,
        provider: str = "google",
        model_name: Optional[str] = None,
        max_papers_to_analyze: int = 10,
        max_idea_generation_attempts: int = 3,
        target_conference: Optional[str] = None
    ):
        """
        Initialize Sensei.
        
        Args:
            domain: Research domain to target
            custom_queries: Custom search queries (overrides domain defaults)
            provider: LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
            model_name: Model name (defaults to provider's best model)
            max_papers_to_analyze: Maximum number of papers to analyze
            max_idea_generation_attempts: Maximum attempts to generate passing idea
            target_conference: Target conference name (e.g., "NeurIPS", "ICLR")
        """
        self.target_conference = target_conference
        self.domain = domain
        self.provider = provider
        self.model_name = model_name
        self.max_papers_to_analyze = max_papers_to_analyze
        self.max_idea_generation_attempts = max_idea_generation_attempts
        
        # Initialize modules
        logger.info(f"Initializing Sensei with domain: {domain.value}, provider: {provider}")
        
        self.harvester = Harvester(
            domain=domain,
            custom_queries=custom_queries,
            max_results_per_query=20
        )
        self.autopsy = Autopsy(provider=provider, model_name=model_name)
        self.synthesizer = Synthesizer(
            provider=provider,
            model_name=model_name,
            target_conference=target_conference
        )
        self.validator = Evaluator(
            provider=provider,
            model_name=model_name,
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        self.refiner = Refiner(provider=provider, model_name=model_name)
        self.reporter = Reporter()
        self.code_generator = CodeGenerator(provider=provider, model_name=model_name)
    
    def harvest_papers(self) -> List[Paper]:
        """Harvest papers from arxiv."""
        logger.info("=" * 80)
        logger.info("MODULE 1: HARVESTER - Fetching papers from arxiv")
        logger.info("=" * 80)
        
        papers = self.harvester.harvest_all()
        logger.info(f"Harvested {len(papers)} unique papers")
        return papers
    
    def analyze_papers(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Extract limitations from papers."""
        logger.info("=" * 80)
        logger.info("MODULE 2: AUTOPSY - Extracting limitations from papers")
        logger.info("=" * 80)
        
        analyses = []
        
        # Limit number of papers to analyze
        papers_to_analyze = papers[:self.max_papers_to_analyze]
        logger.info(f"Analyzing {len(papers_to_analyze)} papers (limited from {len(papers)})")
        
        for i, paper in enumerate(papers_to_analyze, 1):
            logger.info(f"\n[{i}/{len(papers_to_analyze)}] Analyzing: {paper.title[:60]}...")
            
            try:
                analysis = self.autopsy.extract_limitations(paper)
                if analysis:
                    analyses.append(analysis)
                    logger.info("Successfully extracted limitations")
                else:
                    logger.warning("Failed to extract limitations")
            except Exception as e:
                logger.error(f"Error analyzing paper: {e}")
                continue
        
        logger.info(f"\nSuccessfully analyzed {len(analyses)} papers")
        return analyses
    
    def generate_and_validate_idea(
        self,
        analyses: List[PaperAnalysis],
        attempt: int = 1,
        refine_iterations: int = 2
    ) -> tuple[ResearchIdea, Evaluation]:
        """Generate idea and validate it with iterative refinement."""
        logger.info("=" * 80)
        logger.info(f"MODULE 3: SYNTHESIZER - Generating research idea (Attempt {attempt})")
        logger.info("=" * 80)
        
        if not analyses:
            raise ValueError("No paper analyses available for idea generation")
        
        # Step 1: Generate initial idea
        idea = self.synthesizer.generate_idea(analyses)
        logger.info(f"Generated initial idea: {idea.title}")
        
        best_idea = idea
        best_evaluation = None
        best_score = -1
        
        # Step 2-4: Judge-Refine Loop
        for iteration in range(refine_iterations + 1):  # +1 for initial evaluation
            logger.info("=" * 80)
            if iteration == 0:
                logger.info("MODULE 4: EVALUATOR (Judge) - Initial evaluation")
            else:
                logger.info(f"MODULE 4: EVALUATOR (Judge) - Evaluation iteration {iteration}")
            logger.info("=" * 80)
            
            # Judge evaluates the idea
            evaluation = self.validator.evaluate(idea)
            
            logger.info(f"Evaluation Score: {evaluation.score.total_score}/7")
            logger.info(f"Passed Threshold: {evaluation.passed_threshold}")
            
            # Track best idea
            if evaluation.score.total_score > best_score:
                best_score = evaluation.score.total_score
                best_idea = idea
                best_evaluation = evaluation
            
            # If passed, we're done
            if evaluation.passed_threshold:
                logger.info(f"Idea passed threshold after {iteration} refinement iteration(s)")
                return idea, evaluation
            
            # If not last iteration, refine the idea
            if iteration < refine_iterations:
                logger.info("=" * 80)
                logger.info(f"REFINER - Improving idea based on judge feedback (Iteration {iteration + 1})")
                logger.info("=" * 80)
                
                try:
                    # Refiner improves the idea based on judge feedback
                    refined_idea = self.refiner.refine_idea(idea, evaluation)
                    logger.info(f"Refined idea: {refined_idea.title}")
                    idea = refined_idea
                except Exception as e:
                    logger.error(f"Error refining idea: {e}")
                    logger.warning("Continuing with original idea...")
                    break
        
        # Return best idea found
        if best_evaluation:
            logger.info(f"Best idea found with score {best_score}/7")
            return best_idea, best_evaluation
        else:
            return idea, evaluation
    
    def run(self, output_dir: str = "reports") -> Optional[str]:
        """
        Run the complete Autonomous Research Scientist pipeline.
        
        Args:
            output_dir: Directory to save reports
        
        Returns:
            Path to generated report, or None if failed
        """
        try:
            logger.info("=" * 80)
            logger.info("SENSEI - Starting Research Pipeline")
            logger.info("=" * 80)
            
            # Step 1: Harvest papers
            papers = self.harvest_papers()
            if not papers:
                logger.error("No papers harvested. Exiting.")
                return None
            
            # Step 2: Analyze papers
            analyses = self.analyze_papers(papers)
            if not analyses:
                logger.error("No paper analyses generated. Exiting.")
                return None
            
            # Step 3 & 4: Generate and validate idea (with retries)
            best_idea = None
            best_evaluation = None
            best_score = -1
            
            for attempt in range(1, self.max_idea_generation_attempts + 1):
                try:
                    idea, evaluation = self.generate_and_validate_idea(analyses, attempt)
                    
                    if evaluation.score.total_score > best_score:
                        best_score = evaluation.score.total_score
                        best_idea = idea
                        best_evaluation = evaluation
                    
                    # If passed threshold, we're done
                    if evaluation.passed_threshold:
                        logger.info(f"Idea passed threshold on attempt {attempt}")
                        break
                    else:
                        logger.warning(f"Idea failed threshold on attempt {attempt}. Score: {evaluation.score.total_score}/7")
                        if attempt < self.max_idea_generation_attempts:
                            logger.info("Retrying with new idea generation...")
                            # Provide feedback to synthesizer for next attempt
                            self.synthesizer.last_feedback = {
                                "feasibility_score": evaluation.score.feasibility_score,
                                "feasibility_justification": evaluation.score.feasibility_justification,
                                "total_score": evaluation.score.total_score
                            }
                            logger.info(f"Feedback for next attempt: Focus on feasibility - {evaluation.score.feasibility_justification[:150]}...")
                
                except Exception as e:
                    logger.error(f"Error in attempt {attempt}: {e}")
                    if attempt < self.max_idea_generation_attempts:
                        continue
                    else:
                        raise
            
            if not best_idea or not best_evaluation:
                logger.error("Failed to generate any valid idea.")
                return None
            
            # Step 5: Generate report
            logger.info("=" * 80)
            logger.info("MODULE 5: REPORTER - Generating markdown report")
            logger.info("=" * 80)
            
            report_path = self.reporter.save_report(
                best_idea,
                best_evaluation,
                output_dir=output_dir
            )
            
            # Step 6: Generate complete research project code (if idea passed threshold)
            project_path = None
            if best_evaluation.passed_threshold:
                logger.info("=" * 80)
                logger.info("MODULE 6: CODE GENERATOR - Generating complete research project")
                logger.info("=" * 80)
                
                try:
                    project_data = self.code_generator.generate_project_code(
                        idea=best_idea,
                        evaluation=best_evaluation
                    )
                    
                    project_path = self.code_generator.save_project(
                        project_data=project_data,
                        idea=best_idea,
                        output_dir=os.path.join(output_dir, "..", "generated_projects")
                    )
                    
                    logger.info(f"Complete research project generated at: {project_path}")
                    logger.info("Project includes: model code, training scripts, experiments, benchmarks, ablations")
                    
                except Exception as e:
                    logger.error(f"Error generating project code: {e}", exc_info=True)
                    logger.warning("Continuing without project code generation...")
            
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Report saved to: {report_path}")
            logger.info(f"Final Score: {best_evaluation.score.total_score}/7")
            if project_path:
                logger.info(f"Research project code saved to: {project_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            return None


def main():
    """Main entry point."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(
        description="Autonomous Research Scientist - AI-Powered Research Idea Generation"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["google", "anthropic", "openai", "openrouter", "groq", "together"],
        default="google",
        help="LLM provider (default: google)"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Model name (defaults to provider's best model)"
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=[d.name for d in ResearchDomain],
        default="AI_SAFETY",
        help="Research domain (default: AI_SAFETY)"
    )
    parser.add_argument(
        "--custom-queries",
        type=str,
        default=None,
        help="Custom queries file (one query per line)"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=10,
        help="Maximum number of papers to analyze (default: 10)"
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum attempts to generate passing idea (default: 3)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)"
    )
    
    args = parser.parse_args()
    
    # Parse domain
    domain = ResearchDomain[args.domain]
    
    # Parse custom queries if provided
    custom_queries = None
    if args.custom_queries and Path(args.custom_queries).exists():
        with open(args.custom_queries, 'r') as f:
            custom_queries = [line.strip() for line in f if line.strip()]
    
    # Initialize and run
    scientist = Sensei(
        domain=domain,
        custom_queries=custom_queries,
        provider=args.provider,
        model_name=args.model_name,
        max_papers_to_analyze=args.max_papers,
        max_idea_generation_attempts=args.max_attempts
    )
    
    report_path = scientist.run(output_dir=args.output_dir)
    
    if report_path:
        print(f"\nSuccess! Report saved to: {report_path}")
        return 0
    else:
        print("\nPipeline failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit(main())

