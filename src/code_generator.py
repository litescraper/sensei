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
    """Generates complete research project code for approved ideas."""
    
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
            temperature: Temperature for code generation
        """
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        system_template = """You are an expert research engineer specializing in generating complete research codebases.

Generate a complete, working research project implementation based on a research idea that has been approved by an evaluation system.

Requirements:
1. Generate all necessary code files for a research project
2. All code must be runnable and follow best practices
3. Include experiments, benchmarks, ablations, and evaluation code
4. Follow standard ML research project structure
5. Include docstrings, comments, and README
6. Include configuration files, seeds, and clear instructions

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

Guidelines:
- Use PyTorch or TensorFlow
- Include error handling and logging
- Use YAML configs for hyperparameters
- Include data loading, evaluation metrics, visualization
- Add checkpoint saving/loading
- Include seed setting for reproducibility
- Add command-line argument parsing
- Training loop with validation
- Evaluation on test set with metrics
- Compare against baselines
- Include ablation studies

CRITICAL: You MUST output ONLY valid JSON. Do not include any markdown, explanations, or directory trees. Output ONLY the JSON object.

Your output must be a valid JSON object with this exact structure:
{{
    "project_structure": {{
        "src/model.py": "complete code content here",
        "src/trainer.py": "complete code content here",
        "src/evaluator.py": "complete code content here",
        "src/utils.py": "complete code content here",
        "experiments/train.py": "complete code content here",
        "experiments/evaluate.py": "complete code content here",
        "experiments/benchmark.py": "complete code content here",
        "experiments/ablation.py": "complete code content here",
        "configs/default.yaml": "complete YAML content here"
    }},
    "readme_content": "complete README markdown content",
    "requirements": ["torch>=2.0.0", "numpy>=1.24.0", "pandas>=2.0.0"],
    "config_yaml": "complete YAML configuration content",
    "setup_instructions": "step-by-step setup instructions"
}}

Output ONLY the JSON object, nothing else. No markdown, no explanations, no directory trees."""

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

IMPORTANT: Output ONLY valid JSON. Start with {{ and end with }}. Include all code files in the project_structure field as strings. Do not output markdown, directory trees, or explanations - only JSON."""

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
        logger.info("Generating complete research project code...")
        
        if project_name is None:
            # Sanitize idea title for project name
            project_name = "".join(c for c in idea.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            project_name = project_name.replace(' ', '_').lower()[:50]
        
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
        
        import json
        import re
        
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
        
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        lines = content.split('\n')
        json_start = None
        json_end = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().endswith('}'):
                json_end = i + 1
                break
        
        if json_start is not None and json_end is not None:
            content = '\n'.join(lines[json_start:json_end])
        
        try:
            project_data = json.loads(content)
            if "project_structure" not in project_data:
                raise ValueError("Missing 'project_structure' key in JSON response")
            logger.info("Successfully parsed generated project code")
            return project_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content (first 2000 chars): {content[:2000]}...")
            raise ValueError(f"Failed to parse code generation response: {e}")
    
    def save_project(
        self,
        project_data: Dict[str, Any],
        idea: ResearchIdea,
        evaluation: Evaluation,
        output_dir: str = "generated_projects",
        project_name: Optional[str] = None
    ) -> str:
        if project_name is None:
            project_name = "".join(c for c in idea.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            project_name = project_name.replace(' ', '_').lower()[:50]
        
        base_dir = Path(output_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        project_dir = base_dir / project_name
        if project_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_dir = base_dir / f"{project_name}_{timestamp}"
        
        project_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving project to: {project_dir}")
        
        project_structure = project_data.get("project_structure", {})
        for file_path, file_content in project_structure.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            logger.info(f"Saved: {file_path}")
        
        readme_content = project_data.get("readme_content", "")
        if readme_content:
            with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info("Saved: README.md")
        
        requirements = project_data.get("requirements", [])
        if requirements:
            with open(project_dir / "requirements.txt", 'w', encoding='utf-8') as f:
                for req in requirements:
                    f.write(f"{req}\n")
            logger.info("Saved: requirements.txt")
        
        config_yaml = project_data.get("config_yaml", "")
        if config_yaml:
            config_dir = project_dir / "configs"
            config_dir.mkdir(exist_ok=True)
            with open(config_dir / "default.yaml", 'w', encoding='utf-8') as f:
                f.write(config_yaml)
            logger.info("Saved: configs/default.yaml")
        
        setup_instructions = project_data.get("setup_instructions", "")
        if setup_instructions:
            with open(project_dir / "SETUP.md", 'w', encoding='utf-8') as f:
                f.write(setup_instructions)
            logger.info("Saved: SETUP.md")
        
        import json
        with open(project_dir / "idea.json", 'w', encoding='utf-8') as f:
            json.dump({
                "title": idea.title,
                "abstract": idea.abstract,
                "introduction": idea.introduction,
                "method": idea.method,
                "expected_results": idea.expected_results,
                "keywords": idea.keywords
            }, f, indent=2)
        
        with open(project_dir / "evaluation.json", 'w', encoding='utf-8') as f:
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

