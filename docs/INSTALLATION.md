# Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- API keys for selected providers

## Step-by-Step Installation

### 1. Clone Repository

```bash
git clone https://github.com/devadigapratham/sensei.git
cd sensei
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required for Google provider
GOOGLE_API_KEY=your_google_api_key

# Required for Anthropic provider
ANTHROPIC_API_KEY=your_anthropic_api_key

# Required for OpenAI provider
OPENAI_API_KEY=your_openai_api_key

# Required for OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key

# Required for Groq
GROQ_API_KEY=your_groq_api_key

# Required for Together AI
TOGETHER_API_KEY=your_together_api_key

# Optional but recommended
SERPAPI_API_KEY=your_serpapi_key
SEMANTICSCHOLAR_API_KEY=your_semanticscholar_key
```

### 5. Verify Installation

```bash
python -c "from src.main import SheldonCooper; print('Installation successful!')"
```

## Running the Application

### Web UI (Recommended)

```bash
streamlit run app.py
```

Access at `http://localhost:8501`

### Command Line

```bash
python main.py --domain AI_SAFETY --provider google --max-papers 5
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're in the project root directory and the virtual environment is activated.

### API Key Errors

Verify your API keys are correctly set in `.env` file and that they have the necessary permissions.

### Model Not Found Errors

Check that the model name is correct for your provider. See `src/llm_providers.py` for available models.

### PDF Download Errors

Some papers may have restricted access. The system will skip these and continue with others.

