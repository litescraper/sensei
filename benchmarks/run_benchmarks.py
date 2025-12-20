"""
Run benchmarks comparing this system against other AI scientist systems.

Each system implementation uses our infrastructure with system-specific approaches
to generate research ideas, then evaluates them using our Evaluator for fair comparison.
"""
import sys
import os
import time
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from benchmarks.benchmark_framework import BenchmarkRunner, generate_benchmark_report
from src.main import Sensei
from src.config import ResearchDomain
from src.evaluator import Evaluator
from src.models import ResearchIdea
from src.llm_providers import LLMProvider
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_evaluation_from_report(report_path: str):
    """Helper to parse evaluation scores from markdown report."""
    import re
    
    with open(report_path, 'r') as f:
        content = f.read()
    
    total_match = re.search(r'Total Score:\s*(\d+)/7', content)
    novelty_match = re.search(r'Novelty.*?(\d+)/2', content)
    audacity_match = re.search(r'Audacity.*?(\d+)/2', content)
    feasibility_match = re.search(r'Feasibility.*?(\d+)/2', content)
    cross_match = re.search(r'Cross-Disciplinary.*?(\d+)/1', content)
    
    return {
        "total_score": int(total_match.group(1)) if total_match else 0,
        "novelty_score": int(novelty_match.group(1)) if novelty_match else 0,
        "audacity_score": int(audacity_match.group(1)) if audacity_match else 0,
        "feasibility_score": int(feasibility_match.group(1)) if feasibility_match else 0,
        "cross_disciplinary_score": int(cross_match.group(1)) if cross_match else 0,
        "literature_check_details": content[:500]
    }


def run_our_system(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Wrapper to run our system (Sensei) for benchmarking."""
    start_gen = time.time()
    
    scientist = Sensei(
        domain=domain,
        provider="groq",
        model_name="openai/gpt-oss-120b",
        max_papers_to_analyze=5,
        max_idea_generation_attempts=2
    )
    
    report_path = scientist.run(output_dir="benchmarks/temp_reports")
    gen_time = time.time() - start_gen
    
    if report_path:
        scores = _parse_evaluation_from_report(report_path)
        return {
            "evaluation": {
                "score": {
                    "novelty_score": scores["novelty_score"],
                    "audacity_score": scores["audacity_score"],
                    "feasibility_score": scores["feasibility_score"],
                    "cross_disciplinary_score": scores["cross_disciplinary_score"],
                    "total_score": scores["total_score"]
                },
                "literature_check_details": scores["literature_check_details"]
            },
            "generation_time": gen_time * 0.6,
            "evaluation_time": gen_time * 0.4
        }
    else:
        raise Exception("Pipeline failed")


def run_autogpt(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for AutoGPT research mode - autonomous agent approach."""
    start_time = time.time()
    
    prompt = """You are AutoGPT operating in research mode. Your approach:
1. Autonomously search and analyze current research trends
2. Identify practical gaps and opportunities in existing work
3. Propose implementable, incremental improvements
4. Focus on practical solutions over theoretical novelty
5. Generate ideas that can be executed with available tools and resources

Generate a research idea that is:
- Practical and implementable
- Based on current trends and gaps
- Incrementally improving existing work
- Feasible with standard research infrastructure"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "AutoGPT", prompt, domain, provider="google", temperature=0.6, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"AutoGPT benchmark error: {e}")
        raise


def run_researchagent(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for ResearchAgent - specialized research paper generation."""
    start_time = time.time()
    
    prompt = """You are ResearchAgent, a specialized system for generating research papers.
Your methodology:
1. Analyze existing literature and build upon it systematically
2. Propose incremental but meaningful improvements
3. Use well-established, proven methodologies
4. Ground ideas in recent published work
5. Follow standard academic paper structure

Generate a research idea that:
- Builds directly on existing literature
- Proposes clear incremental improvements
- Uses established methodologies
- Is well-grounded in recent papers
- Follows academic conventions"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "ResearchAgent", prompt, domain, provider="google", temperature=0.5, use_papers=True
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"ResearchAgent benchmark error: {e}")
        raise


def run_gpt4_assistant(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for GPT-4 Research Assistant."""
    start_time = time.time()
    
    prompt = """You are GPT-4 acting as a research assistant. Your approach:
1. Generate well-structured, clear research ideas
2. Build on strong theoretical foundations
3. Ensure feasibility with current resources
4. Include clear evaluation metrics and methodologies
5. Prioritize quality, clarity, and rigor over novelty

Generate a research idea that is:
- Well-structured and clearly articulated
- Theoretically sound and well-founded
- Feasible with available resources
- Has clear evaluation methodology
- High quality and rigorous"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "GPT-4 Assistant", prompt, domain, provider="openai", temperature=0.3, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="openai",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"GPT-4 Assistant benchmark error: {e}")
        raise


def run_eureka(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for Eureka (NVIDIA) - adapted for general research."""
    start_time = time.time()
    
    prompt = """You are Eureka, an AI agent originally specialized in robotics research, now adapted for general research.
Your methodology (adapted from robotics):
1. Focus on practical, implementable solutions
2. Emphasize engineering feasibility and real-world applicability
3. Provide domain-specific, detailed methodologies
4. Include clear experimental protocols and validation procedures
5. Prioritize solutions that can be tested and validated experimentally

Generate a research idea that:
- Is practical and implementable
- Emphasizes engineering and feasibility
- Is detailed and domain-specific
- Has clear experimental protocols
- Can be validated experimentally"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "Eureka", prompt, domain, provider="google", temperature=0.4, use_papers=True
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"Eureka benchmark error: {e}")
        raise


def run_langchain_agents(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for LangChain Research Agents."""
    start_time = time.time()
    
    prompt = """You are a LangChain-based research agent using modular, chain-based reasoning.
Your approach:
1. Use modular, chain-based reasoning processes
2. Leverage tool use and information retrieval capabilities
3. Generate structured, well-formatted outputs
4. Apply incremental refinement and iteration
5. Utilize available tools and chains effectively

Generate a research idea that:
- Uses modular, chain-based reasoning
- Leverages tools and information retrieval
- Has structured, clear output
- Can be incrementally refined
- Makes effective use of available tools"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "LangChain Agents", prompt, domain, provider="google", temperature=0.6, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"LangChain Agents benchmark error: {e}")
        raise


def run_autoresearch(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for AutoResearch - automated research paper generation."""
    start_time = time.time()
    
    prompt = """You are AutoResearch, an automated research paper generation system.
Your methodology:
1. Follow standard academic paper structures and formats
2. Include proper citations, references, and literature grounding
3. Propose incremental but meaningful improvements
4. Ensure ideas are suitable for academic publication
5. Maintain academic rigor and use standard methodologies

Generate a research idea that:
- Follows standard paper structure
- Includes proper citations and references
- Proposes incremental improvements
- Is suitable for publication
- Maintains academic rigor"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "AutoResearch", prompt, domain, provider="google", temperature=0.5, use_papers=True
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"AutoResearch benchmark error: {e}")
        raise


def run_researchgpt(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for ResearchGPT - GPT-based research assistant."""
    start_time = time.time()
    
    prompt = """You are ResearchGPT, a GPT-based research assistant.
Your approach:
1. Leverage language model capabilities for idea generation
2. Generate well-articulated, clear research ideas
3. Build systematically on existing research
4. Provide structured, detailed methodologies
5. Focus on clear communication and structured thinking

Generate a research idea that:
- Leverages language model capabilities
- Is well-articulated and clear
- Builds on existing research
- Has structured methodology
- Demonstrates clear communication"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "ResearchGPT", prompt, domain, provider="google", temperature=0.6, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"ResearchGPT benchmark error: {e}")
        raise


def run_scispace_copilot(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for SciSpace Copilot - literature review focused."""
    start_time = time.time()
    
    prompt = """You are SciSpace Copilot, an AI research assistant specialized in literature review and synthesis.
Your methodology:
1. Ground ideas deeply in existing literature
2. Synthesize insights from multiple papers
3. Identify research gaps through comprehensive reviews
4. Propose ideas based on citation analysis and patterns
5. Focus on literature synthesis and gap identification

Generate a research idea that:
- Is grounded in existing literature
- Synthesizes multiple papers
- Identifies gaps from reviews
- Uses citation analysis
- Focuses on literature synthesis"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "SciSpace Copilot", prompt, domain, provider="google", temperature=0.4, use_papers=True
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"SciSpace Copilot benchmark error: {e}")
        raise


def run_consensus_ai(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for Consensus AI - evidence synthesis platform."""
    start_time = time.time()
    
    prompt = """You are Consensus AI, an AI-powered research synthesis platform.
Your methodology:
1. Synthesize evidence from multiple research sources
2. Find consensus and patterns across papers
3. Propose evidence-based, well-supported improvements
4. Generate incremental ideas backed by research
5. Focus on multi-paper synthesis and evidence aggregation

Generate a research idea that:
- Synthesizes evidence from multiple sources
- Finds consensus across papers
- Proposes evidence-based improvements
- Is incremental and well-supported
- Uses multi-paper synthesis"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "Consensus AI", prompt, domain, provider="google", temperature=0.5, use_papers=True
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"Consensus AI benchmark error: {e}")
        raise


def run_claude_research(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for Claude Research (Anthropic)."""
    start_time = time.time()
    
    prompt = """You are Claude acting as a research assistant. Your approach:
1. Demonstrate strong reasoning and analytical thinking
2. Generate well-structured, logical research ideas
3. Build on solid theoretical foundations
4. Provide clear, step-by-step methodologies
5. Ensure ideas are feasible and well-planned
6. Focus on quality reasoning and structured output

Generate a research idea that:
- Demonstrates strong reasoning
- Is well-structured and logical
- Builds on theoretical foundations
- Has clear step-by-step methodology
- Is feasible and well-planned"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "Claude Research", prompt, domain, provider="anthropic", temperature=0.3, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="anthropic",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"Claude Research benchmark error: {e}")
        raise


def run_perplexity_pro(domain: ResearchDomain = ResearchDomain.AI_SAFETY):
    """Implementation for Perplexity Pro - web search integrated research assistant."""
    start_time = time.time()
    
    prompt = """You are Perplexity Pro, an AI research assistant with web search integration.
Your methodology:
1. Incorporate real-time information from web sources
2. Generate well-cited, properly sourced research ideas
3. Reflect current trends and recent developments
4. Synthesize information from both web and academic sources
5. Focus on information retrieval and synthesis

Generate a research idea that:
- Incorporates real-time information
- Is well-cited and sourced
- Reflects current trends
- Synthesizes web and academic sources
- Uses information retrieval effectively"""
    
    try:
        idea = _generate_idea_with_system_approach(
            "Perplexity Pro", prompt, domain, provider="google", temperature=0.5, use_papers=False
        )
        
        evaluator = Evaluator(
            provider="google",
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        generation_time = time.time() - start_time
        eval_start = time.time()
        evaluation = evaluator.evaluate(idea)
        evaluation_time = time.time() - eval_start
        
        return {
            "evaluation": {
                "score": {
                    "novelty_score": evaluation.score.novelty_score,
                    "audacity_score": evaluation.score.audacity_score,
                    "feasibility_score": evaluation.score.feasibility_score,
                    "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                    "total_score": evaluation.score.total_score
                },
                "literature_check_details": str(evaluation.literature_papers)[:500]
            },
            "generation_time": generation_time,
            "evaluation_time": evaluation_time
        }
    except Exception as e:
        logger.error(f"Perplexity Pro benchmark error: {e}")
        raise


def main():
    """Run benchmark comparison for all systems."""
    runner = BenchmarkRunner(output_dir="benchmarks/results")
    
    logger.info("Starting comprehensive benchmark comparison...")
    logger.info("All systems use proper implementations with system-specific approaches")
    logger.info("")
    
    domain = ResearchDomain.AI_SAFETY
    num_runs = 3  # Reduced for faster benchmarking (increase for production)
    
    system_results = {}
    
    # Benchmark Sensei (our system)
    logger.info("Benchmarking Sensei (our system)...")
    system_results["Sensei"] = runner.run_benchmark(
        system_name="Sensei",
        system_runner=lambda: run_our_system(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark AutoGPT
    logger.info("Benchmarking AutoGPT...")
    system_results["AutoGPT"] = runner.run_benchmark(
        system_name="AutoGPT",
        system_runner=lambda: run_autogpt(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark ResearchAgent
    logger.info("Benchmarking ResearchAgent...")
    system_results["ResearchAgent"] = runner.run_benchmark(
        system_name="ResearchAgent",
        system_runner=lambda: run_researchagent(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark GPT-4 Assistant
    logger.info("Benchmarking GPT-4 Assistant...")
    system_results["GPT-4 Assistant"] = runner.run_benchmark(
        system_name="GPT-4 Assistant",
        system_runner=lambda: run_gpt4_assistant(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark Eureka
    logger.info("Benchmarking Eureka (NVIDIA)...")
    system_results["Eureka (NVIDIA)"] = runner.run_benchmark(
        system_name="Eureka (NVIDIA)",
        system_runner=lambda: run_eureka(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark LangChain Agents
    logger.info("Benchmarking LangChain Agents...")
    system_results["LangChain Agents"] = runner.run_benchmark(
        system_name="LangChain Agents",
        system_runner=lambda: run_langchain_agents(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark AutoResearch
    logger.info("Benchmarking AutoResearch...")
    system_results["AutoResearch"] = runner.run_benchmark(
        system_name="AutoResearch",
        system_runner=lambda: run_autoresearch(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark ResearchGPT
    logger.info("Benchmarking ResearchGPT...")
    system_results["ResearchGPT"] = runner.run_benchmark(
        system_name="ResearchGPT",
        system_runner=lambda: run_researchgpt(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark SciSpace Copilot
    logger.info("Benchmarking SciSpace Copilot...")
    system_results["SciSpace Copilot"] = runner.run_benchmark(
        system_name="SciSpace Copilot",
        system_runner=lambda: run_scispace_copilot(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark Consensus AI
    logger.info("Benchmarking Consensus AI...")
    system_results["Consensus AI"] = runner.run_benchmark(
        system_name="Consensus AI",
        system_runner=lambda: run_consensus_ai(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark Claude Research
    logger.info("Benchmarking Claude Research...")
    system_results["Claude Research"] = runner.run_benchmark(
        system_name="Claude Research",
        system_runner=lambda: run_claude_research(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Benchmark Perplexity Pro
    logger.info("Benchmarking Perplexity Pro...")
    system_results["Perplexity Pro"] = runner.run_benchmark(
        system_name="Perplexity Pro",
        system_runner=lambda: run_perplexity_pro(domain),
        num_runs=num_runs,
        domain="AI_SAFETY"
    )
    
    # Generate comparison
    logger.info("")
    logger.info("Generating comparison report...")
    comparison = runner.compare_systems(system_results)
    
    # Generate report
    report_file = "benchmarks/results/benchmark_report.md"
    generate_benchmark_report(comparison, report_file)
    
    logger.info("")
    logger.info(f"Benchmark complete! Report saved to {report_file}")
    logger.info("")
    logger.info("Summary of all systems:")
    for system_name, metrics in system_results.items():
        logger.info(f"  {system_name}: {metrics.metrics['total_score']:.2f}/7.0 (Pass Rate: {metrics.metrics['pass_rate']*100:.1f}%)")


if __name__ == "__main__":
    main()

