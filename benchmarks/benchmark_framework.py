"""
Benchmarking Framework for Autonomous Research Scientist

Compares against existing AI scientist systems:
- AutoGPT (Research mode)
- ResearchAgent
- AutoResearch
- Eureka (for robotics, adapted)
- Other research generation systems
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BenchmarkMetrics:
    """Metrics for evaluating research idea generation systems."""
    
    def __init__(self):
        self.metrics = {
            "novelty_score": 0.0,  # Average novelty score (0-2)
            "audacity_score": 0.0,  # Average audacity score (0-2)
            "feasibility_score": 0.0,  # Average feasibility score (0-2)
            "cross_disciplinary_score": 0.0,  # Average cross-disciplinary score (0-1)
            "total_score": 0.0,  # Average total score (0-7)
            "pass_rate": 0.0,  # Percentage of ideas scoring >= 5/7
            "literature_overlap": 0.0,  # Average similarity to existing papers (0-1)
            "generation_time": 0.0,  # Average time to generate idea (seconds)
            "evaluation_time": 0.0,  # Average time to evaluate idea (seconds)
            "total_time": 0.0,  # Average total pipeline time (seconds)
            "ideas_generated": 0,  # Total number of ideas generated
            "papers_analyzed": 0,  # Total number of papers analyzed
            "success_rate": 0.0,  # Percentage of successful pipeline runs
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return self.metrics.copy()
    
    def update(self, **kwargs):
        """Update metrics with new values."""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value


class BenchmarkRunner:
    """
    Benchmark runner for comparing against other AI scientist systems.
    
    Evaluates:
    1. Idea Quality (Novelty, Audacity, Feasibility)
    2. Literature Grounding (Overlap with existing work)
    3. Efficiency (Generation time, evaluation time)
    4. Success Rate (Pipeline completion rate)
    """
    
    def __init__(self, output_dir: str = "benchmarks/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[Dict[str, Any]] = []
    
    def run_benchmark(
        self,
        system_name: str,
        system_runner,
        num_runs: int = 10,
        domain: Optional[str] = None
    ) -> BenchmarkMetrics:
        """
        Run benchmark for a given system.
        
        Args:
            system_name: Name of the system being benchmarked
            system_runner: Callable that runs the system and returns results
            num_runs: Number of benchmark runs
            domain: Research domain (optional)
        """
        logger.info(f"Starting benchmark for {system_name}")
        
        metrics = BenchmarkMetrics()
        all_scores = {
            "novelty": [],
            "audacity": [],
            "feasibility": [],
            "cross_disciplinary": [],
            "total": [],
            "generation_times": [],
            "evaluation_times": [],
            "total_times": [],
            "literature_overlaps": [],
        }
        
        successful_runs = 0
        
        for run_id in range(num_runs):
            logger.info(f"Run {run_id + 1}/{num_runs} for {system_name}")
            
            try:
                start_time = time.time()
                result = system_runner()
                total_time = time.time() - start_time
                
                if result and "evaluation" in result:
                    eval_data = result["evaluation"]
                    score = eval_data.get("score", {})
                    
                    all_scores["novelty"].append(score.get("novelty_score", 0))
                    all_scores["audacity"].append(score.get("audacity_score", 0))
                    all_scores["feasibility"].append(score.get("feasibility_score", 0))
                    all_scores["cross_disciplinary"].append(score.get("cross_disciplinary_score", 0))
                    all_scores["total"].append(score.get("total_score", 0))
                    
                    all_scores["generation_times"].append(result.get("generation_time", 0))
                    all_scores["evaluation_times"].append(result.get("evaluation_time", 0))
                    all_scores["total_times"].append(total_time)
                    
                    # Calculate literature overlap (simplified)
                    lit_check = eval_data.get("literature_check_details", "")
                    overlap = self._calculate_literature_overlap(lit_check)
                    all_scores["literature_overlaps"].append(overlap)
                    
                    successful_runs += 1
                    
                    # Save individual result
                    self.results.append({
                        "system": system_name,
                        "run_id": run_id,
                        "domain": domain,
                        "timestamp": datetime.now().isoformat(),
                        "result": result
                    })
                
            except Exception as e:
                logger.error(f"Benchmark run {run_id + 1} failed: {e}")
                continue
        
        # Calculate averages
        if successful_runs > 0:
            metrics.update(
                novelty_score=self._average(all_scores["novelty"]),
                audacity_score=self._average(all_scores["audacity"]),
                feasibility_score=self._average(all_scores["feasibility"]),
                cross_disciplinary_score=self._average(all_scores["cross_disciplinary"]),
                total_score=self._average(all_scores["total"]),
                pass_rate=self._pass_rate(all_scores["total"]),
                literature_overlap=self._average(all_scores["literature_overlaps"]),
                generation_time=self._average(all_scores["generation_times"]),
                evaluation_time=self._average(all_scores["evaluation_times"]),
                total_time=self._average(all_scores["total_times"]),
                ideas_generated=successful_runs,
                success_rate=successful_runs / num_runs
            )
        
        # Save benchmark results
        self._save_results(system_name, metrics, domain)
        
        return metrics
    
    def _calculate_literature_overlap(self, lit_check: str) -> float:
        """
        Calculate literature overlap score.
        
        Lower is better (less overlap = more novel).
        """
        if not lit_check:
            return 0.0
        
        # Count number of related papers found
        # More papers = higher overlap
        paper_count = lit_check.count("[")
        
        # Normalize to 0-1 scale (assuming max 20 papers)
        return min(paper_count / 20.0, 1.0)
    
    def _average(self, values: List[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def _pass_rate(self, scores: List[float]) -> float:
        """Calculate pass rate (scores >= 5/7)."""
        if not scores:
            return 0.0
        passing = sum(1 for s in scores if s >= 5.0)
        return passing / len(scores)
    
    def _save_results(self, system_name: str, metrics: BenchmarkMetrics, domain: Optional[str]):
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{system_name}_{domain or 'all'}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        result_data = {
            "system": system_name,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics.to_dict()
        }
        
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Saved benchmark results to {filepath}")
    
    def compare_systems(self, system_results: Dict[str, BenchmarkMetrics]) -> Dict[str, Any]:
        """
        Compare multiple systems and generate comparison report.
        
        Args:
            system_results: Dictionary mapping system names to their metrics
        
        Returns:
            Comparison report dictionary
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "rankings": {}
        }
        
        # Collect metrics for each system
        for system_name, metrics in system_results.items():
            comparison["systems"][system_name] = metrics.to_dict()
        
        # Rank systems by total score
        sorted_systems = sorted(
            system_results.items(),
            key=lambda x: x[1].metrics["total_score"],
            reverse=True
        )
        
        comparison["rankings"]["by_total_score"] = [
            {"system": name, "score": metrics.metrics["total_score"]}
            for name, metrics in sorted_systems
        ]
        
        # Rank by pass rate
        sorted_by_pass = sorted(
            system_results.items(),
            key=lambda x: x[1].metrics["pass_rate"],
            reverse=True
        )
        
        comparison["rankings"]["by_pass_rate"] = [
            {"system": name, "pass_rate": metrics.metrics["pass_rate"]}
            for name, metrics in sorted_by_pass
        ]
        
        # Rank by efficiency (lower time is better)
        sorted_by_time = sorted(
            system_results.items(),
            key=lambda x: x[1].metrics["total_time"]
        )
        
        comparison["rankings"]["by_efficiency"] = [
            {"system": name, "total_time": metrics.metrics["total_time"]}
            for name, metrics in sorted_by_time
        ]
        
        # Save comparison
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = self.output_dir / f"comparison_{timestamp}.json"
        
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"Saved comparison report to {comparison_file}")
        
        return comparison


def generate_benchmark_report(comparison: Dict[str, Any], output_file: str):
    """Generate human-readable benchmark report."""
    
    report = f"""# Benchmark Comparison Report

Generated: {comparison['timestamp']}

## Systems Evaluated

"""
    
    for system_name, metrics in comparison["systems"].items():
        report += f"""### {system_name}

**Quality Metrics:**
- Novelty Score: {metrics['novelty_score']:.2f}/2.0
- Audacity Score: {metrics['audacity_score']:.2f}/2.0
- Feasibility Score: {metrics['feasibility_score']:.2f}/2.0
- Cross-Disciplinary Score: {metrics['cross_disciplinary_score']:.1f}/1.0
- **Total Score: {metrics['total_score']:.2f}/7.0**

**Performance Metrics:**
- Pass Rate (≥5/7): {metrics['pass_rate']*100:.1f}%
- Literature Overlap: {metrics['literature_overlap']:.2f}
- Generation Time: {metrics['generation_time']:.2f}s
- Evaluation Time: {metrics['evaluation_time']:.2f}s
- Total Time: {metrics['total_time']:.2f}s
- Success Rate: {metrics['success_rate']*100:.1f}%

**Volume:**
- Ideas Generated: {metrics['ideas_generated']}
- Papers Analyzed: {metrics['papers_analyzed']}

---

"""
    
    # Rankings
    report += """## Rankings

### By Total Score (Quality)
"""
    for i, entry in enumerate(comparison["rankings"]["by_total_score"], 1):
        report += f"{i}. {entry['system']}: {entry['score']:.2f}/7.0\n"
    
    report += "\n### By Pass Rate\n"
    for i, entry in enumerate(comparison["rankings"]["by_pass_rate"], 1):
        report += f"{i}. {entry['system']}: {entry['pass_rate']*100:.1f}%\n"
    
    report += "\n### By Efficiency (Total Time)\n"
    for i, entry in enumerate(comparison["rankings"]["by_efficiency"], 1):
        report += f"{i}. {entry['system']}: {entry['total_time']:.2f}s\n"
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Generated benchmark report: {output_file}")

