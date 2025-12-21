"""
Module 6: Code Generator - Research Project Generator

Generates complete, working research project code when an idea passes evaluation.
Includes experiments, architecture, benchmarks, ablations, and all components needed for a paper.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from .models import ResearchIdea, Evaluation
from .llm_providers import LLMProvider

logger = logging.getLogger(__name__)


class CodeGenerator:
    """
    Generates complete research project code for approved ideas.
    
    Creates:
    - Model/architecture implementation
    - Training scripts
    - Evaluation scripts
    - Experiment infrastructure
    - Benchmark code
    - Ablation study code
    - Configuration files
    - README and documentation
    - Requirements file
    """
    
    def __init__(
        self,
        provider: str = "google",
        model_name: Optional[str] = None,
        temperature: float = 0.3  # Lower temperature for code generation
    ):
        """
        Initialize the Code Generator.
        
        Args:
            provider: LLM provider
            model_name: Model name
            temperature: Temperature for code generation (default: 0.3 for more deterministic code)
        """
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        # Build code generation prompt
        system_template = """You are an expert research engineer specializing in generating complete, production-ready research codebases for machine learning papers.

Your task is to generate a complete, working research project implementation based on a research idea that has been approved by an evaluation system.

CRITICAL REQUIREMENTS:
1. **Complete Implementation**: Generate ALL necessary code files for a research project
2. **Working Code**: All code must be runnable and follow best practices
3. **Paper-Ready**: Include experiments, benchmarks, ablations, and evaluation code
4. **Well-Structured**: Follow standard ML research project structure
5. **Documented**: Include docstrings, comments, and README
6. **Reproducible**: Include configuration files, seeds, and clear instructions

PROJECT STRUCTURE TO GENERATE:
```
project_name/
├── src/
│   ├── __init__.py
│   ├── model.py          # Main model/architecture implementation
│   ├── trainer.py        # Training script
│   ├── evaluator.py      # Evaluation script
│   └── utils.py          # Utility functions
├── experiments/
│   ├── __init__.py
│   ├── train.py          # Main training experiment
│   ├── evaluate.py      # Evaluation experiment
│   ├── benchmark.py     # Benchmark script
│   └── ablation.py      # Ablation study script
├── configs/
│   └── default.yaml     # Configuration file
├── data/
│   └── README.md        # Data instructions
├── requirements.txt      # Python dependencies
├── README.md            # Project README
└── setup.py             # Setup script (optional)
```

CODE GENERATION GUIDELINES:
1. Use PyTorch or TensorFlow (specify which)
2. Include proper error handling
3. Add logging throughout
4. Use configuration files (YAML) for hyperparameters
5. Include data loading utilities
6. Add evaluation metrics
7. Include visualization/plotting code
8. Add checkpoint saving/loading
9. Include seed setting for reproducibility
10. Add command-line argument parsing

EXPERIMENT CODE REQUIREMENTS:
- Training loop with validation
- Evaluation on test set
- Metric computation (accuracy, F1, etc. as appropriate)
- Logging (TensorBoard or similar)
- Checkpoint management
- Early stopping (if applicable)

BENCHMARK CODE REQUIREMENTS:
- Compare against baseline methods
- Standard datasets
- Fair comparison setup
- Statistical significance testing
- Results visualization

ABLATION CODE REQUIREMENTS:
- Systematically remove/modify components
- Compare configurations
- Generate comparison tables/plots
- Statistical analysis

Your output should be a JSON object with the following structure:
{{
    "project_structure": {{
        "src/model.py": "complete code content",
        "src/trainer.py": "complete code content",
        ...
    }},
    "readme_content": "complete README markdown",
    "requirements": ["package1>=version", "package2>=version", ...],
    "config_yaml": "complete YAML configuration",
    "setup_instructions": "step-by-step setup instructions"
}}

Generate code that is:
- Production-ready and runnable
- Well-documented
- Following best practices
- Suitable for paper submission
- Reproducible"""

        human_template = """RESEARCH IDEA:

Title: {idea_title}

Abstract: {idea_abstract}

Introduction: {idea_introduction}

Method: {idea_method}

Expected Results: {idea_expected_results}

Keywords: {idea_keywords}

EVALUATION FEEDBACK:

Overall Summary: {evaluation_summary}

Score: {total_score}/7
- Novelty: {novelty_score}/2 - {novelty_justification}
- Audacity: {audacity_score}/2 - {audacity_justification}
- Feasibility: {feasibility_score}/2 - {feasibility_justification}
- Cross-disciplinary: {cross_disciplinary_score}/1 - {cross_disciplinary_justification}

De-risking Experiments: {de_risking_experiments}

Based on this approved research idea, generate a complete, working research project codebase.
Output the JSON structure with all code files, README, requirements, and configuration.

IMPORTANT: Generate actual, runnable code. Do not use placeholders or TODOs unless absolutely necessary."""

        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def generate_project_code(
        self,
        idea: ResearchIdea,
        evaluation: Evaluation,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete research project code.
        
        Args:
            idea: Approved research idea
            evaluation: Evaluation result
            project_name: Name for the project (default: sanitized idea title)
        
        Returns:
            Dictionary with project structure and files
        """
        logger.info("Generating complete research project code...")
        
        if project_name is None:
            # Sanitize idea title for project name
            project_name = "".join(c for c in idea.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            project_name = project_name.replace(' ', '_').lower()[:50]
        
        # Format de-risking experiments
        de_risking_str = "\n".join(f"- {exp}" for exp in evaluation.de_risking_experiments)
        if not de_risking_str:
            de_risking_str = "None specified"
        
        messages = self.prompt.format_messages(
            idea_title=idea.title,
            idea_abstract=idea.abstract,
            idea_introduction=idea.introduction,
            idea_method=idea.method,
            idea_expected_results=idea.expected_results,
            idea_keywords=", ".join(idea.keywords),
            evaluation_summary=evaluation.overall_summary,
            total_score=evaluation.score.total_score,
            novelty_score=evaluation.score.novelty_score,
            novelty_justification=evaluation.score.novelty_justification[:200],
            audacity_score=evaluation.score.audacity_score,
            audacity_justification=evaluation.score.audacity_justification[:200],
            feasibility_score=evaluation.score.feasibility_score,
            feasibility_justification=evaluation.score.feasibility_justification[:200],
            cross_disciplinary_score=evaluation.score.cross_disciplinary_score,
            cross_disciplinary_justification=evaluation.score.cross_disciplinary_justification[:200],
            de_risking_experiments=de_risking_str
        )
        
        response = self.llm.invoke(messages)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Try to extract JSON
        import json
        import re
        
        # Extract JSON from response
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
        
        # Try to find JSON object
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        try:
            project_data = json.loads(content)
            logger.info("Successfully parsed generated project code")
            return project_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content (first 1000 chars): {content[:1000]}...")
            raise ValueError(f"Failed to parse code generation response: {e}")
    
    def save_project(
        self,
        project_data: Dict[str, Any],
        idea: ResearchIdea,
        output_dir: str = "generated_projects",
        project_name: Optional[str] = None
    ) -> str:
        """
        Save generated project to disk.
        
        Args:
            project_data: Generated project data from LLM
            idea: Research idea
            output_dir: Base output directory
            project_name: Project name (default: sanitized title)
        
        Returns:
            Path to generated project directory
        """
        if project_name is None:
            project_name = "".join(c for c in idea.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            project_name = project_name.replace(' ', '_').lower()[:50]
        
        # Create project directory
        base_dir = Path(output_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        project_dir = base_dir / project_name
        if project_dir.exists():
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_dir = base_dir / f"{project_name}_{timestamp}"
        
        project_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving project to: {project_dir}")
        
        # Save project structure files
        project_structure = project_data.get("project_structure", {})
        for file_path, file_content in project_structure.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            logger.info(f"Saved: {file_path}")
        
        # Save README
        readme_content = project_data.get("readme_content", "")
        if readme_content:
            readme_path = project_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info(f"Saved: README.md")
        
        # Save requirements.txt
        requirements = project_data.get("requirements", [])
        if requirements:
            req_path = project_dir / "requirements.txt"
            with open(req_path, 'w', encoding='utf-8') as f:
                for req in requirements:
                    f.write(f"{req}\n")
            logger.info(f"Saved: requirements.txt")
        
        # Save config YAML
        config_yaml = project_data.get("config_yaml", "")
        if config_yaml:
            config_dir = project_dir / "configs"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "default.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_yaml)
            logger.info(f"Saved: configs/default.yaml")
        
        # Save setup instructions
        setup_instructions = project_data.get("setup_instructions", "")
        if setup_instructions:
            setup_path = project_dir / "SETUP.md"
            with open(setup_path, 'w', encoding='utf-8') as f:
                f.write(setup_instructions)
            logger.info(f"Saved: SETUP.md")
        
        # Save original idea and evaluation for reference
        import json
        idea_path = project_dir / "idea.json"
        with open(idea_path, 'w', encoding='utf-8') as f:
            json.dump({
                "title": idea.title,
                "abstract": idea.abstract,
                "introduction": idea.introduction,
                "method": idea.method,
                "expected_results": idea.expected_results,
                "keywords": idea.keywords
            }, f, indent=2)
        
        eval_path = project_dir / "evaluation.json"
        with open(eval_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_score": evaluation.score.total_score,
                "novelty_score": evaluation.score.novelty_score,
                "audacity_score": evaluation.score.audacity_score,
                "feasibility_score": evaluation.score.feasibility_score,
                "cross_disciplinary_score": evaluation.score.cross_disciplinary_score,
                "passed_threshold": evaluation.passed_threshold,
                "overall_summary": evaluation.overall_summary,
                "de_risking_experiments": evaluation.de_risking_experiments
            }, f, indent=2)
        
        logger.info(f"Project saved successfully to: {project_dir}")
        return str(project_dir)

