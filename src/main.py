"""
Main orchestration script for Sheldon Cooper - Autonomous Research Scientist.

Sheldon Cooper is an autonomous research system that generates novel research ideas
in AI Safety, Trustworthy AI, Adversarial Machine Learning, and Jailbreaking domains
using the strict Lossfunk Framework for evaluation.
"""
import os
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

from .harvester import Harvester
from .autopsy import Autopsy
from .synthesizer import Synthesizer
from .evaluator import LossfunkEvaluator
from .reporter import Reporter
from .config import ResearchDomain
from .models import (
    Paper,
    PaperAnalysis,
    ResearchIdea,
    LossfunkEvaluation,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SheldonCooper:
    """
    Main orchestration class for the Autonomous Research Scientist.
    
    Named after the brilliant theoretical physicist, this system autonomously:
    1. Harvests recent research papers from arxiv
    2. Extracts limitations and vulnerabilities
    3. Synthesizes novel research ideas
    4. Validates ideas using the Lossfunk Framework
    5. Generates comprehensive research reports
    """
    
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
        Initialize Sheldon Cooper.
        
        Args:
            domain: Research domain to target
            custom_queries: Custom search queries (overrides domain defaults)
            provider: LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
            model_name: Model name (defaults to provider's best model)
            max_papers_to_analyze: Maximum number of papers to analyze
            max_idea_generation_attempts: Maximum attempts to generate passing idea
            target_conference: Target conference name (e.g., "ICML", "NeurIPS")
        """
        self.target_conference = target_conference
        self.domain = domain
        self.provider = provider
        self.model_name = model_name
        self.max_papers_to_analyze = max_papers_to_analyze
        self.max_idea_generation_attempts = max_idea_generation_attempts
        
        # Initialize modules
        logger.info(f"Initializing Sheldon Cooper with domain: {domain.value}, provider: {provider}")
        
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
        self.validator = LossfunkEvaluator(
            provider=provider,
            model_name=model_name,
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        self.reporter = Reporter()
    
    def harvest_papers(self) -> List[Paper]:
        """Step 1: Harvest papers from arxiv."""
        logger.info("=" * 80)
        logger.info("MODULE 1: HARVESTER - Fetching papers from arxiv")
        logger.info("=" * 80)
        
        papers = self.harvester.harvest_all()
        logger.info(f"Harvested {len(papers)} unique papers")
        return papers
    
    def analyze_papers(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Step 2: Extract limitations from papers."""
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
        attempt: int = 1
    ) -> tuple[ResearchIdea, LossfunkEvaluation]:
        """Step 3 & 4: Generate idea and validate it."""
        logger.info("=" * 80)
        logger.info(f"MODULE 3: SYNTHESIZER - Generating research idea (Attempt {attempt})")
        logger.info("=" * 80)
        
        if not analyses:
            raise ValueError("No paper analyses available for idea generation")
        
        # Generate idea
        idea = self.synthesizer.generate_idea(analyses, attempt)
        logger.info(f"Generated idea: {idea.title}")
        
        logger.info("=" * 80)
        logger.info("MODULE 4: LOSSFUNK VALIDATOR - Evaluating idea")
        logger.info("=" * 80)
        
        # Validate idea
        evaluation = self.validator.evaluate(idea)
        
        logger.info(f"Evaluation Score: {evaluation.score.total_score}/7")
        logger.info(f"Passed Threshold: {evaluation.passed_threshold}")
        
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
            logger.info("SHELDON COOPER - Starting Research Pipeline")
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
            
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Report saved to: {report_path}")
            logger.info(f"Final Score: {best_evaluation.score.total_score}/7")
            
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
    scientist = SheldonCooper(
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

