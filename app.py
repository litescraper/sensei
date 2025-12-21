import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Optional, List
import time
import warnings
import logging

# Suppress warnings
logging.getLogger("streamlit.watcher").setLevel(logging.ERROR)
logging.getLogger("streamlit.web.bootstrap").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*torch.*")
warnings.filterwarnings("ignore", message=".*__path__.*")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import Sensei
from src.config import ResearchDomain, ModelProvider, Conference
from src.llm_providers import AVAILABLE_MODELS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Sensei - Autonomous Research Scientist",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, stunning CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        background-color: #ffffff;
    }
    
    /* Ensure all text is visible */
    .main {
        background-color: #ffffff;
        color: #1f2937;
    }
    
    /* Markdown text visibility */
    .main p, .main li, .main div[data-testid="stMarkdownContainer"] p,
    .main div[data-testid="stMarkdownContainer"] li,
    .main div[data-testid="stMarkdownContainer"] {
        color: #1f2937 !important;
    }
    
    /* Headers visibility */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
    .main div[data-testid="stMarkdownContainer"] h1,
    .main div[data-testid="stMarkdownContainer"] h2,
    .main div[data-testid="stMarkdownContainer"] h3,
    .main div[data-testid="stMarkdownContainer"] h4,
    .main div[data-testid="stMarkdownContainer"] h5,
    .main div[data-testid="stMarkdownContainer"] h6 {
        color: #1f2937 !important;
    }
    
    /* Lists visibility */
    .main ul, .main ol,
    .main div[data-testid="stMarkdownContainer"] ul,
    .main div[data-testid="stMarkdownContainer"] ol {
        color: #1f2937 !important;
    }
    
    .main ul li, .main ol li,
    .main div[data-testid="stMarkdownContainer"] ul li,
    .main div[data-testid="stMarkdownContainer"] ol li {
        color: #1f2937 !important;
    }
    
    /* Strong and emphasis */
    .main strong, .main b,
    .main div[data-testid="stMarkdownContainer"] strong,
    .main div[data-testid="stMarkdownContainer"] b {
        color: #1f2937 !important;
    }
    
    /* Stunning header */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 4rem 3rem;
        border-radius: 24px;
        margin: -1rem -1rem 3rem -1rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        margin: 1rem 0 0 0;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Modern cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-card h3 {
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
    }
    
    .feature-card p {
        color: #6b7280;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem 0.5rem 0.25rem 0;
    }
    
    .status-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        border: 1px solid #10b981;
    }
    
    .status-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border: 1px solid #ef4444;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button * {
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stButton > button:hover * {
        color: white !important;
    }
    
    .stButton > button:active {
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stButton > button:active * {
        color: white !important;
    }
    
    .stButton > button:focus {
        color: white !important;
    }
    
    .stButton > button:focus * {
        color: white !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .info-box strong {
        color: #1f2937 !important;
        font-weight: 600;
    }
    
    .info-box {
        color: #1f2937 !important;
    }
    
    .info-box p, .info-box div {
        color: #1f2937 !important;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
    }
    
    .success-box h2 {
        color: #065f46;
        margin: 0 0 1rem 0;
        font-weight: 700;
        font-size: 2rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 800;
        color: white !important;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        letter-spacing: -0.02em;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8fafc;
    }
    
    /* Metric cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #667eea;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)


def check_api_keys(provider: str) -> dict:
    """Check which API keys are configured."""
    keys = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY"),
    }
    
    if provider == "anthropic":
        keys["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
    elif provider == "openai":
        keys["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    elif provider == "openrouter":
        keys["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    elif provider == "groq":
        keys["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    elif provider == "together":
        keys["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")
    
    return {k: bool(v) for k, v in keys.items()}


def main():
    """Main Streamlit application."""
    
    # Stunning hero header
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Sensei</h1>
        <p class="hero-subtitle">Autonomous Research Scientist</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### Configuration")
        st.markdown("---")
        
        # Research Domain Selection - Custom input
        st.markdown("#### Research Domain")
        domain_mode = st.radio(
            "Domain selection mode",
            options=["Custom Domain", "Predefined Domain"],
            index=0,
            label_visibility="collapsed"
        )
        
        selected_domain = None
        custom_queries = None
        custom_domain_name = ""
        
        if domain_mode == "Custom Domain":
            st.markdown("**Enter your research domain:**")
            custom_domain_name = st.text_input(
                "Domain name",
                placeholder="e.g., Quantum Machine Learning",
                label_visibility="collapsed"
            )
            
            st.markdown("**Describe your research interests (natural language):**")
            natural_language_input = st.text_area(
                "Natural language description",
                placeholder="e.g., I'm interested in combining graph neural networks with reinforcement learning for multi-agent systems. I want to explore how GNNs can improve coordination in decentralized environments.",
                height=100,
                label_visibility="collapsed",
                help="Describe your research interests in natural language. The system will generate search queries automatically."
            )
            
            st.markdown("**Or provide search queries directly (one per line):**")
            query_text = st.text_area(
                "Queries",
                placeholder="graph neural networks reinforcement learning\nmulti-agent systems coordination\ndecentralized learning",
                height=100,
                label_visibility="collapsed"
            )
            
            if natural_language_input and not query_text:
                try:
                    query_generation_prompt = f"""Based on the following research interest description, generate 3-5 specific search queries for arXiv paper search.

Research Interest: {natural_language_input}

Generate search queries that are:
- Specific and focused
- Suitable for arXiv paper search
- Cover different aspects of the research interest
- Use technical terminology

Return only the queries, one per line, without numbering or bullets."""
                    from src.llm_providers import LLMProvider
                    llm = LLMProvider.create_llm(provider=provider, model_name=model_name, temperature=0.7)
                    response = llm.invoke(query_generation_prompt)
                    generated_queries = response.content if hasattr(response, 'content') else str(response)
                    custom_queries = [q.strip() for q in generated_queries.split("\n") if q.strip() and not q.strip().startswith("#")]
                    if custom_queries:
                        st.info(f"Generated queries: {', '.join(custom_queries[:3])}...")
                except Exception as e:
                    st.warning(f"Could not generate queries from natural language: {e}. Please provide queries directly.")
                    custom_queries = None
            elif query_text:
                custom_queries = [q.strip() for q in query_text.split("\n") if q.strip()]
            else:
                custom_queries = None
            
            if custom_domain_name and custom_queries:
                selected_domain = ResearchDomain.CUSTOM
        else:
            domain_options = {d.value: d for d in ResearchDomain if d != ResearchDomain.CUSTOM}
            selected_domain_str = st.selectbox(
                "Choose predefined domain",
                options=list(domain_options.keys()),
                index=0,
                label_visibility="collapsed"
            )
            selected_domain = domain_options[selected_domain_str]
        
        st.markdown("---")
        
        # LLM Provider Selection
        st.markdown("#### AI Model Provider")
        provider = st.selectbox(
            "Provider",
            options=["google", "anthropic", "openai", "openrouter", "groq", "together"],
            index=4,  # Default to Groq
            label_visibility="collapsed"
        )
        
        # Model Selection
        available_models = AVAILABLE_MODELS.get(provider, [])
        if available_models:
            default_index = 0
            if provider == "groq":
                # Prefer GPT OSS 120B
                if "openai/gpt-oss-120b" in available_models:
                    default_index = available_models.index("openai/gpt-oss-120b")
                elif "llama-3.1-70b-versatile" in available_models:
                    default_index = available_models.index("llama-3.1-70b-versatile")
            elif provider == "google" and "gemini-2.5-flash" in available_models:
                default_index = available_models.index("gemini-2.5-flash")
            
            model_name = st.selectbox(
                "Model",
                options=available_models,
                index=default_index,
                label_visibility="collapsed"
            )
        else:
            model_name = st.text_input(
                "Model name",
                value="llama-3.1-70b-versatile" if provider == "groq" else "",
                label_visibility="collapsed"
            )
            if not model_name:
                model_name = None
        
        st.markdown("---")
        
        # Conference Selection
        st.markdown("#### Target Conference")
        conference_options = {c.value: c.value for c in Conference}
        selected_conference = st.selectbox(
            "Choose target conference",
            options=list(conference_options.keys()),
            index=len(conference_options) - 1,  # Default to "General"
            label_visibility="collapsed",
            help="Select the conference you want to target for your research idea"
        )
        
        st.markdown("---")
        
        # Pipeline Settings
        st.markdown("#### Pipeline Settings")
        max_papers = st.slider(
            "Max papers to analyze",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of papers to extract limitations from"
        )
        
        max_attempts = st.slider(
            "Max idea generation attempts",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of attempts to generate a passing idea"
        )
        
        st.markdown("---")
        
        # API Keys Status
        st.markdown("#### API Keys Status")
        api_keys_status = check_api_keys(provider)
        for key_name, status in api_keys_status.items():
            if status:
                st.markdown(f'<span class="status-badge status-success">✓ {key_name}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-badge status-error">✗ {key_name}</span>', unsafe_allow_html=True)
        
        if not all(api_keys_status.values()):
            st.warning("Some API keys are missing. Please set them in .env file")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Run Pipeline", "Validate Idea", "Results", "Documentation", "About"])
    
    with tab1:
        st.markdown('<div class="section-header">Start Research Pipeline</div>', unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>Harvest Papers</h3>
                <p>Automatically fetch recent papers from arXiv in your selected domain with intelligent filtering.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Extract Insights</h3>
                <p>Deep analysis extracts methods, strengths, limitations, and potential solutions from each paper.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>Generate Ideas</h3>
                <p>Intelligently combine insights to create novel, audacious, and feasible research ideas.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### How It Works
            
            This system autonomously:
            
            1. **Harvest** papers from arxiv in your selected domain
            2. **Extract** comprehensive analysis including methods, strengths, limitations, and solutions
            3. **Synthesize** novel research ideas by intelligently combining insights
            4. **Evaluate** ideas using a comprehensive scoring framework
            5. **Generate** comprehensive research reports with detailed feedback
            
            Click the button below to start generating novel research ideas.
            """)
        
        with col2:
            st.markdown("### Current Configuration")
            if selected_domain:
                domain_display = custom_domain_name if domain_mode == "Custom Domain" and custom_domain_name else (selected_domain.value if hasattr(selected_domain, 'value') else str(selected_domain))
                st.markdown(f"""
                <div class="info-box">
                    <strong>Domain:</strong><br>
                    {domain_display[:50]}...
                </div>
                <div class="info-box">
                    <strong>Provider:</strong><br>
                    {provider.upper()}
                </div>
                <div class="info-box">
                    <strong>Model:</strong><br>
                    {model_name or "Default"}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Run button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            run_button = st.button(
                "Start Research Pipeline",
                type="primary",
                use_container_width=True
            )
        
        if run_button:
            if not selected_domain or (domain_mode == "Custom Domain" and not custom_queries):
                st.error("Please configure your research domain and queries before running the pipeline.")
            elif not all(api_keys_status.values()):
                st.error("Please configure all required API keys in .env file before running the pipeline.")
            else:
                run_pipeline(selected_domain, custom_queries, provider, model_name, max_papers, max_attempts, selected_conference)
    
    with tab2:
        st.markdown('<div class="section-header">Validate Research Idea</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Validate Your Research Idea
        
        Have a research idea you'd like to validate? Enter it below and Sensei will evaluate it using the same comprehensive framework used for generated ideas.
        
        This will help you understand:
        - **Novelty**: How novel is your idea compared to existing work?
        - **Audacity**: How impactful could this be if successful?
        - **Feasibility**: Is this achievable with current resources?
        - **Cross-disciplinary impact**: Does it bridge multiple fields?
        - **Detailed feedback**: Specific suggestions for improvement
        - **De-risking experiments**: Concrete experiments to validate your idea
        """)
        
        st.markdown("---")
        
        idea_title = st.text_input(
            "Research Idea Title *",
            placeholder="e.g., Graph Neural Networks for Multi-Agent Reinforcement Learning",
            help="Enter a clear, descriptive title for your research idea"
        )
        
        idea_abstract = st.text_area(
            "Abstract *",
            placeholder="Provide a brief abstract (2-3 sentences) describing your research idea...",
            height=100,
            help="Brief summary of your research idea"
        )
        
        idea_introduction = st.text_area(
            "Introduction / Background",
            placeholder="Describe the problem, motivation, and background context...",
            height=120,
            help="Context and motivation for your research idea"
        )
        
        idea_method = st.text_area(
            "Method / Approach *",
            placeholder="Describe your proposed method, approach, or technique...",
            height=120,
            help="Your proposed methodology"
        )
        
        idea_expected_results = st.text_area(
            "Expected Results",
            placeholder="What results do you expect? What would success look like?",
            height=100,
            help="Expected outcomes and success criteria"
        )
        
        idea_keywords = st.text_input(
            "Keywords (comma-separated)",
            placeholder="graph neural networks, reinforcement learning, multi-agent systems",
            help="Keywords for literature search"
        )
        
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            validate_button = st.button(
                "Validate Idea",
                type="primary",
                use_container_width=True
            )
        
        if validate_button:
            if not idea_title or not idea_abstract or not idea_method:
                st.error("Please fill in at least Title, Abstract, and Method fields (marked with *).")
            elif not all(api_keys_status.values()):
                st.error("Please configure all required API keys in .env file.")
            else:
                validate_idea(
                    idea_title, idea_abstract, idea_introduction, 
                    idea_method, idea_expected_results, idea_keywords,
                    provider, model_name, selected_conference
                )
    
    with tab3:
        st.markdown('<div class="section-header">Previous Results</div>', unsafe_allow_html=True)
        display_results()
    
    with tab4:
        st.markdown('<div class="section-header">Documentation</div>', unsafe_allow_html=True)
        display_documentation()
    
    with tab5:
        st.markdown('<div class="section-header">About Sensei</div>', unsafe_allow_html=True)
        display_about()


def run_pipeline(
    domain: ResearchDomain,
    custom_queries: Optional[List[str]],
    provider: str,
    model_name: Optional[str],
    max_papers: int,
    max_attempts: int,
    target_conference: str
):
    """Run the research pipeline with professional progress tracking."""
    
    progress_container = st.container()
    status_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.markdown("### Pipeline Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Step 1: Initialize
        with status_container:
            with st.expander("Initialization", expanded=True):
                status_text.markdown("**Status:** Initializing pipeline...")
                progress_bar.progress(0.1)
                time.sleep(0.5)
        
        scientist = Sensei(
            domain=domain,
            custom_queries=custom_queries,
            provider=provider,
            model_name=model_name,
            max_papers_to_analyze=max_papers,
            max_idea_generation_attempts=max_attempts,
            target_conference=target_conference
        )
        
        # Step 2: Run pipeline
        with status_container:
            with st.expander("Running Pipeline", expanded=True):
                status_text.markdown("**Status:** Pipeline running... This may take a few minutes.")
                progress_bar.progress(0.3)
        
        report_path = scientist.run(output_dir="reports")
        
        progress_bar.progress(1.0)
        
        # Step 3: Results
        with results_container:
            if report_path:
                st.markdown("""
                <div class="success-box">
                    <h2>Pipeline Completed Successfully</h2>
                    <p>Your research idea has been generated and evaluated.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display report
                with open(report_path, 'r') as f:
                    report_content = f.read()
                
                # Download button
                col1, col_btn, col3 = st.columns([1, 2, 1])
                with col_btn:
                    st.download_button(
                        label="Download Report",
                        data=report_content,
                        file_name=Path(report_path).name,
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                # Report preview
                st.markdown("### Report Preview")
                with st.expander("View Full Report", expanded=False):
                    st.markdown(report_content)
                
                # Show key metrics if available
                st.markdown("### Key Metrics")
                st.info("Check the full report for detailed evaluation scores and feedback.")
                
            else:
                st.error("Pipeline failed. Check logs for details.")
    
    except Exception as e:
        with status_container:
            st.error(f"Error: {str(e)}")
            with st.expander("Error Details"):
                st.exception(e)


def display_results():
    """Display previous results with professional cards."""
    reports_dir = Path("reports")
    if reports_dir.exists():
        reports = sorted(reports_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if reports:
            st.markdown(f"### Found {len(reports)} Report(s)")
            
            for i, report in enumerate(reports[:10]):
                with st.expander(f"{report.name}", expanded=(i == 0)):
                    with open(report, 'r') as f:
                        content = f.read()
                    
                    # Show preview
                    preview = content[:1000] + "..." if len(content) > 1000 else content
                    st.markdown(preview)
                    
                    # Download button
                    st.download_button(
                        "Download Full Report",
                        data=content,
                        file_name=report.name,
                        key=f"dl_{report.name}_{i}",
                        use_container_width=True
                    )
        else:
            st.info("No reports yet. Run the pipeline to generate your first research idea.")
    else:
        st.info("Reports directory not found. Run the pipeline to create reports.")


def display_documentation():
    """Display documentation with actual markdown content."""
    st.markdown("### Documentation")
    
    doc_files = {
        "Architecture": "docs/ARCHITECTURE.md",
        "How It Works": "docs/HOW_IT_WORKS.md",
        "Theory": "docs/THEORY.md",
        "API Reference": "docs/API_REFERENCE.md",
        "Installation": "docs/INSTALLATION.md",
    }
    
    selected_doc = st.selectbox(
        "Select documentation to view",
        options=list(doc_files.keys()),
        index=0
    )
    
    doc_path = Path(doc_files[selected_doc])
    if doc_path.exists():
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        st.markdown(content)
    else:
        st.error(f"Documentation file not found: {doc_path}")
    
    st.markdown("---")
    st.markdown("### Quick Start")
    st.markdown("""
    1. Configure your API keys in `.env` file
    2. Select your research domain, target conference, and AI model
    3. Click "Start Research Pipeline"
    4. Download your generated research report
    """)


def validate_idea(
    title: str,
    abstract: str,
    introduction: str,
    method: str,
    expected_results: str,
    keywords: str,
    provider: str,
    model_name: Optional[str],
    target_conference: str
):
    """Validate a user-provided research idea."""
    from src.models import ResearchIdea
    from src.evaluator import Evaluator
    from src.reporter import Reporter
    import os
    
    progress_container = st.container()
    status_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.markdown("### Validation Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        with status_container:
            with st.expander("Initialization", expanded=True):
                status_text.markdown("**Status:** Initializing evaluator...")
                progress_bar.progress(0.1)
                time.sleep(0.3)
        
        evaluator = Evaluator(
            provider=provider,
            model_name=model_name,
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            semanticscholar_key=os.getenv("SEMANTICSCHOLAR_API_KEY")
        )
        
        keywords_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
        
        idea = ResearchIdea(
            title=title,
            abstract=abstract,
            introduction=introduction or "No introduction provided.",
            method=method,
            expected_results=expected_results or "No expected results specified.",
            keywords=keywords_list
        )
        
        with status_container:
            with st.expander("Evaluating Idea", expanded=True):
                status_text.markdown("**Status:** Evaluating your research idea... This may take a minute.")
                progress_bar.progress(0.3)
        
        evaluation = evaluator.evaluate(idea)
        
        progress_bar.progress(1.0)
        
        with results_container:
            st.markdown("""
            <div class="success-box">
                <h2>Evaluation Complete</h2>
                <p>Your research idea has been evaluated.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Score", f"{evaluation.score.total_score}/7")
            
            with col2:
                st.metric("Novelty", f"{evaluation.score.novelty_score}/2")
            
            with col3:
                st.metric("Audacity", f"{evaluation.score.audacity_score}/2")
            
            with col4:
                st.metric("Feasibility", f"{evaluation.score.feasibility_score}/2")
            
            st.markdown("---")
            
            st.markdown("### Detailed Scores")
            
            score_col1, score_col2 = st.columns(2)
            
            with score_col1:
                st.markdown(f"""
                **Novelty ({evaluation.score.novelty_score}/2)**
                
                {evaluation.score.novelty_justification}
                """)
                
                st.markdown(f"""
                **Audacity ({evaluation.score.audacity_score}/2)**
                
                {evaluation.score.audacity_justification}
                """)
            
            with score_col2:
                st.markdown(f"""
                **Feasibility ({evaluation.score.feasibility_score}/2)**
                
                {evaluation.score.feasibility_justification}
                """)
                
                st.markdown(f"""
                **Cross-Disciplinary ({evaluation.score.cross_disciplinary_score}/1)**
                
                {evaluation.score.cross_disciplinary_justification}
                """)
            
            st.markdown("---")
            
            st.markdown("### Overall Summary")
            st.markdown(evaluation.overall_summary)
            
            if evaluation.feedback_table:
                st.markdown("---")
                st.markdown("### Feedback and Suggestions")
                
                for i, feedback in enumerate(evaluation.feedback_table, 1):
                    with st.expander(f"Feedback {i}: {feedback.weakness}", expanded=(i == 1)):
                        st.markdown(f"""
                        **Novelty Improvement:**
                        {feedback.thinking_prompt_novelty}
                        
                        **Audacity Improvement:**
                        {feedback.thinking_prompt_audacity}
                        
                        **Feasibility Improvement:**
                        {feedback.thinking_prompt_feasibility}
                        
                        **Why Important:**
                        {feedback.why_important}
                        """)
            
            if evaluation.de_risking_experiments:
                st.markdown("---")
                st.markdown("### De-risking Experiments")
                for i, exp in enumerate(evaluation.de_risking_experiments, 1):
                    st.markdown(f"{i}. {exp}")
            
            if evaluation.literature_papers:
                st.markdown("---")
                st.markdown("### Related Literature")
                st.markdown(f"Found {len(evaluation.literature_papers)} related papers:")
                for paper in evaluation.literature_papers[:10]:
                    st.markdown(f"- {paper}")
            
            st.markdown("---")
            
            reporter = Reporter()
            report_path = reporter.save_report(idea, evaluation, output_dir="reports")
            
            if report_path:
                with open(report_path, 'r') as f:
                    report_content = f.read()
                
                col1, col_btn, col3 = st.columns([1, 2, 1])
                with col_btn:
                    st.download_button(
                        label="Download Full Evaluation Report",
                        data=report_content,
                        file_name=Path(report_path).name,
                        mime="text/markdown",
                        use_container_width=True
                    )
    
    except Exception as e:
        with status_container:
            st.error(f"Error: {str(e)}")
            with st.expander("Error Details"):
                st.exception(e)


def display_about():
    """Display about information."""
    st.markdown("""
    ### About Sensei
    
    **Sensei** is an AI-powered system that autonomously generates and evaluates novel research ideas 
    using a comprehensive evaluation framework.
    
    ### Key Features
    
    - **Multi-Domain Support**: Support for any research domain via custom queries
    - **Multi-Provider LLM**: Support for 6+ AI model providers
    - **Rigorous Evaluation**: 7-point scoring rubric across multiple dimensions
    - **Comprehensive Literature Search**: Multi-source validation
    - **Professional UI**: Modern, user-friendly interface
    
    ### How It Works
    
    1. **Harvest**: Fetches recent papers from arXiv
    2. **Extract**: Identifies limitations and vulnerabilities
    3. **Synthesize**: Generates novel ideas by intersecting limitations
    4. **Evaluate**: Validates ideas using strict criteria
    5. **Report**: Generates comprehensive markdown reports
    
    ### Citation
    
    If you use Sensei in your research, please cite:
    
    ```bibtex
    @software{sensei2025,
      title={Sensei: Autonomous Research Scientist},
      author={Devadiga, Prathamesh},
      year={2025},
      url={https://github.com/devadigapratham/sensei}
    }
    ```
    
    ### License
    
    This project is licensed under the MIT License.
    """)


if __name__ == "__main__":
    main()
