"""
Tests for CodeGenerator module.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.code_generator import CodeGenerator
from src.models import ResearchIdea, Evaluation, Score
from tests.conftest import sample_research_idea, mock_env_vars


class TestCodeGenerator:
    """Test CodeGenerator class."""
    
    def test_code_generator_initialization(self, mock_env_vars):
        """Test CodeGenerator initialization."""
        generator = CodeGenerator(provider="groq", model_name="llama-3.3-70b-versatile")
        assert generator.llm is not None
    
    def test_generate_project_code_success(self, sample_research_idea, mock_env_vars):
        """Test successful project code generation."""
        score = Score(
            novelty_score=2,
            audacity_score=2,
            feasibility_score=2,
            cross_disciplinary_score=1,
            total_score=7,
            novelty_justification="",
            audacity_justification="",
            feasibility_justification="",
            cross_disciplinary_justification=""
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[],
            overall_summary="Great idea",
            de_risking_experiments=["Experiment 1"]
        )
        
        # Mock LLM response with valid JSON
        mock_response = MagicMock()
        mock_response.content = '''{
            "project_structure": {
                "src/model.py": "import torch\\nclass Model(torch.nn.Module):\\n    pass",
                "src/trainer.py": "def train():\\n    pass",
                "experiments/train.py": "if __name__ == '__main__':\\n    train()"
            },
            "readme_content": "# Project README",
            "requirements": ["torch>=2.0.0", "numpy>=1.24.0"],
            "config_yaml": "model:\\n  name: test",
            "setup_instructions": "1. Install dependencies\\n2. Run training"
        }'''
        
        # Mock the LLM before creating CodeGenerator
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.code_generator.LLMProvider.create_llm', return_value=mock_llm):
            generator = CodeGenerator(provider="groq")
            project_data = generator.generate_project_code(sample_research_idea, evaluation)
        
        assert project_data is not None
        assert "project_structure" in project_data
        assert "src/model.py" in project_data["project_structure"]
        assert "requirements" in project_data
    
    def test_generate_project_code_json_extraction(self, sample_research_idea, mock_env_vars):
        """Test JSON extraction from markdown code blocks."""
        score = Score(
            novelty_score=2,
            audacity_score=2,
            feasibility_score=2,
            cross_disciplinary_score=1,
            total_score=7,
            novelty_justification="",
            audacity_justification="",
            feasibility_justification="",
            cross_disciplinary_justification=""
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[],
            overall_summary="Great idea",
            de_risking_experiments=[]
        )
        
        # Mock LLM response with JSON in markdown code block
        mock_response = MagicMock()
        mock_response.content = '''Here's the project structure:
```json
{
    "project_structure": {
        "src/model.py": "code here"
    },
    "readme_content": "README",
    "requirements": ["torch"],
    "config_yaml": "config: value",
    "setup_instructions": "Setup steps"
}
```'''
        
        # Mock the LLM before creating CodeGenerator
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        
        with patch('src.code_generator.LLMProvider.create_llm', return_value=mock_llm):
            generator = CodeGenerator(provider="groq")
            project_data = generator.generate_project_code(sample_research_idea, evaluation)
        
        assert project_data is not None
        assert "project_structure" in project_data
    
    def test_save_project(self, sample_research_idea, mock_env_vars, tmp_path):
        """Test saving generated project to disk."""
        score = Score(
            novelty_score=2,
            audacity_score=2,
            feasibility_score=2,
            cross_disciplinary_score=1,
            total_score=7,
            novelty_justification="",
            audacity_justification="",
            feasibility_justification="",
            cross_disciplinary_justification=""
        )
        
        evaluation = Evaluation(
            score=score,
            feedback_table=[],
            overall_summary="Great idea",
            de_risking_experiments=[]
        )
        
        project_data = {
            "project_structure": {
                "src/model.py": "import torch",
                "src/__init__.py": "",
                "experiments/train.py": "def train(): pass"
            },
            "readme_content": "# Test Project",
            "requirements": ["torch>=2.0.0"],
            "config_yaml": "model: test",
            "setup_instructions": "Install and run"
        }
        
        generator = CodeGenerator(provider="groq")
        project_path = generator.save_project(
            project_data=project_data,
            idea=sample_research_idea,
            evaluation=evaluation,
            output_dir=str(tmp_path)
        )
        
        assert Path(project_path).exists()
        assert (Path(project_path) / "README.md").exists()
        assert (Path(project_path) / "requirements.txt").exists()
        assert (Path(project_path) / "src" / "model.py").exists()
        assert (Path(project_path) / "idea.json").exists()
        assert (Path(project_path) / "evaluation.json").exists()

