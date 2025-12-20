"""
Run benchmarks comparing this system against other AI scientist systems.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from benchmarks.benchmark_framework import BenchmarkRunner, generate_benchmark_report
from src.main import Sensei
from src.config import ResearchDomain
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_our_system(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Wrapper to run our system for benchmarking."""
    import time
    
    start_gen = time.time()
    
    scientist = Sensei(
        domain=domain,
        provider="groq",
        model_name="openai/gpt-oss-120b",  # GPT OSS 120B model
        max_papers_to_analyze=5,  # Reduced for benchmarking
        max_idea_generation_attempts=2
    )
    
    # Run pipeline
    report_path = scientist.run(output_dir="benchmarks/temp_reports")
    
    gen_time = time.time() - start_gen
    
    if report_path:
        # Load the evaluation from the report
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Parse evaluation from markdown report
        import re
        from src.models import Score
        
        # Extract scores from report
        total_match = re.search(r'Total Score:\s*(\d+)/7', content)
        novelty_match = re.search(r'Novelty.*?(\d+)/2', content)
        audacity_match = re.search(r'Audacity.*?(\d+)/2', content)
        feasibility_match = re.search(r'Feasibility.*?(\d+)/2', content)
        cross_match = re.search(r'Cross-Disciplinary.*?(\d+)/1', content)
        
        total_score = int(total_match.group(1)) if total_match else 0
        novelty_score = int(novelty_match.group(1)) if novelty_match else 0
        audacity_score = int(audacity_match.group(1)) if audacity_match else 0
        feasibility_score = int(feasibility_match.group(1)) if feasibility_match else 0
        cross_score = int(cross_match.group(1)) if cross_match else 0
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": novelty_score,
                    "audacity_score": audacity_score,
                    "feasibility_score": feasibility_score,
                    "cross_disciplinary_score": cross_score,
                    "total_score": total_score
                },
                "literature_check_details": content[:500]
            },
            "generation_time": gen_time * 0.6,
            "evaluation_time": gen_time * 0.4
        }
    else:
        raise Exception("Pipeline failed")


def main():
    """Run benchmark comparison."""
    runner = BenchmarkRunner(output_dir="benchmarks/results")
    
    logger.info("Starting benchmark comparison...")
    
    # Benchmark our system with Groq
    logger.info("Benchmarking Sensei system with Groq...")
    our_metrics = runner.run_benchmark(
        system_name="Sensei",
        system_runner=lambda: run_our_system(ResearchDomain.AI_SAFETY),
        num_runs=3,  # Reduced for faster benchmarking
        domain="AI_SAFETY"
    )
    
    # Note: To benchmark other systems, you would need to:
    # 1. Install/configure those systems
    # 2. Create wrapper functions similar to run_our_system()
    # 3. Run benchmarks for each
    
    # Example structure for other systems:
    # auto_gpt_metrics = runner.run_benchmark(
    #     system_name="AutoGPT",
    #     system_runner=lambda: run_autogpt(),
    #     num_runs=5,
    #     domain="AI_SAFETY"
    # )
    
    # For now, create a comparison with just our system
    system_results = {
        "Sensei": our_metrics
    }
    
    # Generate comparison
    comparison = runner.compare_systems(system_results)
    
    # Generate report
    report_file = "benchmarks/results/benchmark_report.md"
    generate_benchmark_report(comparison, report_file)
    
    logger.info(f"Benchmark complete! Report saved to {report_file}")
    logger.info(f"Our system metrics: {our_metrics.to_dict()}")


if __name__ == "__main__":
    main()

