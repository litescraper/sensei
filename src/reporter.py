"""
Module 5: The Reporter

Generates comprehensive markdown reports of research candidates.
Includes evaluation scores, feedback, and de-risking experiments.
Matches the exact template format from the evaluation protocol.
"""
from datetime import datetime
from typing import Optional
import logging
import os
from pathlib import Path
from .models import ResearchIdea, Evaluation

logger = logging.getLogger(__name__)


class Reporter:
    """
    Generates markdown reports for research candidates.
    
    Creates comprehensive reports including:
    - Complete research idea details
    - Evaluation scores and feedback
    - Literature check results
    - Feedback and improvement suggestions
    - De-risking experiment designs
    """
    
    def generate_markdown_report(
        self,
        idea: ResearchIdea,
        evaluation: Evaluation,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate a markdown report for a research candidate.
        
        Args:
            idea: ResearchIdea object
            evaluation: Evaluation object
            timestamp: Timestamp for filename (defaults to now)
        
        Returns:
            Markdown report string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Build markdown report matching the template format
        report_lines = [
            "# Research Candidate Report",
            "",
            f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Research Idea",
            "",
            f"### {idea.title}",
            "",
            "#### Abstract",
            idea.abstract,
            "",
            "#### Introduction",
            idea.introduction,
            "",
            "#### Method",
            idea.method,
            "",
            "#### Expected Results",
            idea.expected_results,
            "",
            "#### Keywords",
            ", ".join(idea.keywords),
            "",
            "---",
            "",
            "## Evaluation Results",
            "",
            "### Step 0: Literature Quick-Scan (Grounding)",
            "",
            evaluation.literature_summary,
            "",
            "**Papers Found:**",
            "",
        ]
        
        # Add literature papers
        if evaluation.literature_papers:
            for paper in evaluation.literature_papers[:20]:  # Limit to top 20
                report_lines.append(f"- {paper}")
        else:
            report_lines.append("- No papers found in literature search.")
        
        report_lines.extend([
            "",
            "### Step 1 & 2: Scoring and Total Score",
            "",
            f"**Total Score:** {evaluation.score.total_score}/7",
            f"**Passed Threshold (≥5/7):** {'YES' if evaluation.passed_threshold else 'NO'}",
            "",
            "#### Score Breakdown",
            "",
            "| Category | Score | Justification |",
            "|----------|-------|---------------|",
            f"| **Novelty** | {evaluation.score.novelty_score}/2 | {evaluation.score.novelty_justification} |",
            f"| **Audacity** | {evaluation.score.audacity_score}/2 | {evaluation.score.audacity_justification} |",
            f"| **Feasibility** | {evaluation.score.feasibility_score}/2 | {evaluation.score.feasibility_justification} |",
            f"| **Cross-Disciplinary** | {evaluation.score.cross_disciplinary_score}/1 | {evaluation.score.cross_disciplinary_justification} |",
            "",
            "### Step 3: Overall Summary and Feedback",
            "",
            evaluation.overall_summary,
            "",
            "#### Feedback Table",
            "",
            "| Weakness | Thinking Prompt (Novelty) | Thinking Prompt (Audacity) | Thinking Prompt (Feasibility) | Why Important |",
            "|----------|-------------------------|----------------------------|------------------------------|---------------|",
        ])
        
        # Add feedback rows with new format
        for feedback in evaluation.feedback_table:
            report_lines.append(
                f"| {feedback.weakness} | {feedback.thinking_prompt_novelty} | "
                f"{feedback.thinking_prompt_audacity} | {feedback.thinking_prompt_feasibility} | "
                f"{feedback.why_important} |"
            )
        
        report_lines.extend([
            "",
            "### Step 4: Unanswered Questions and De-Risking Experiments",
            "",
            "#### Key Unanswered Questions",
            "",
        ])
        
        # Add unanswered questions
        if evaluation.unanswered_questions:
            for question in evaluation.unanswered_questions:
                report_lines.append(f"- {question}")
        else:
            report_lines.append("- No specific unanswered questions identified.")
        
        report_lines.extend([
            "",
            "#### De-Risking Experiments",
            "",
        ])
        
        # Add de-risking experiments
        if evaluation.de_risking_experiments:
            for i, experiment in enumerate(evaluation.de_risking_experiments, 1):
                report_lines.append(f"**Experiment {i}:**")
                report_lines.append("")
                report_lines.append("```python")
                report_lines.append(experiment)
                report_lines.append("```")
                report_lines.append("")
        else:
            report_lines.append("No specific de-risking experiments provided.")
        
        report_lines.extend([
            "---",
            "",
            "## Conclusion",
            "",
            f"This research idea {'PASSES' if evaluation.passed_threshold else 'FAILS'} the evaluation threshold.",
            "",
            f"**Recommendation:** {'Proceed with further development' if evaluation.passed_threshold else 'Revise idea or generate new candidate'}",
        ])
        
        report = "\n".join(report_lines)
        return report
    
    def save_report(
        self,
        idea: ResearchIdea,
        evaluation: Evaluation,
        output_dir: str = "reports",
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Save markdown report to file.
        
        Args:
            idea: ResearchIdea object
            evaluation: Evaluation object
            output_dir: Directory to save report
            timestamp: Timestamp for filename
        
        Returns:
            Path to saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename (sanitize title)
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in idea.title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        filename = f"research_candidate_{timestamp_str}_{safe_title}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Generate and save report
        report = self.generate_markdown_report(idea, evaluation, timestamp)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to {filepath}")
        return filepath

