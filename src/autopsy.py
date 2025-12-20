"""
Module 2: The Autopsy - Intelligent Extraction
Extracts "admission of failure" from papers.
"""
import fitz  # PyMuPDF
import requests
from typing import Optional
import logging
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import tiktoken
from .models import Paper, PaperAnalysis
from .llm_providers import LLMProvider

logger = logging.getLogger(__name__)


class Autopsy:
    """
    Extracts limitations and vulnerabilities from research papers.
    
    Uses configurable LLM providers to analyze paper text and extract explicit
    limitations, unsolved problems, and brittleness mentions.
    """
    
    # Maximum tokens to process (focus on Discussion/Conclusion)
    MAX_TOKENS = 3000
    
    def __init__(
        self,
        provider: str = "google",
        model_name: Optional[str] = None,
        temperature: float = 0.1
    ):
        """
        Initialize the Autopsy with configurable LLM backend.
        
        Args:
            provider: LLM provider ("google", "anthropic", "openai", "openrouter", "groq", "together")
            model_name: Specific model name (defaults to provider's best model)
            temperature: Temperature for LLM generation (default: 0.1 for consistency)
        """
        self.llm = LLMProvider.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature
        )
        
        # Initialize output parser
        self.output_parser = PydanticOutputParser(pydantic_object=PaperAnalysis)
        
        # Build the comprehensive extraction prompt
        system_template = """You are an expert research analyst specializing in understanding research papers deeply and identifying opportunities for improvement.

Your task is to comprehensively analyze this research paper and extract:

1. MAIN CONTRIBUTION: What is the core contribution of this paper? What problem does it solve?
2. METHODOLOGY: What is the key methodology, approach, or technique used? How does it work?
3. KEY TECHNIQUES: List specific techniques, algorithms, or methods employed (e.g., "attention mechanisms", "adversarial training", "reinforcement learning").
4. STRENGTHS: What does this paper do well? What are its novel contributions, advantages, or strong points?
5. EXPLICIT LIMITATIONS: Where do the authors explicitly admit their method fails or has weaknesses?
6. UNSOLVED PROBLEMS: Specific gaps mentioned in Future Work sections or Discussion.
7. VULNERABILITIES: Any mention of hyperparameters being sensitive, method being fragile, or requiring specific conditions.
8. SUGGESTED IMPROVEMENTS: Based on the limitations, what are concrete ways to improve this method?
9. POTENTIAL SOLUTIONS: What approaches or techniques from other domains could address the identified problems?

CRITICAL INSTRUCTIONS:
- Understand the paper deeply: What it does, how it works, why it matters.
- Be specific and actionable. Extract concrete information, not vague statements.
- For suggested improvements and solutions, think creatively about:
  * How to combine techniques from different papers
  * How to address limitations using complementary methods
  * What modifications would make the method more robust
  * What cross-disciplinary approaches could help
- Focus on actionable insights that could lead to novel research ideas.
- If a category has no relevant information, return an empty list or appropriate default.

Output your comprehensive analysis as a JSON object matching the PaperAnalysis schema."""
        
        human_template = """Paper Title: {paper_title}

Paper Abstract: {paper_abstract}

Paper Text (truncated to last 3000 tokens focusing on Discussion/Conclusion): {paper_text}

{format_instructions}"""
        
        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-4o")
            return len(encoding.encode(text))
        except:
            # Fallback: rough estimate
            return len(text.split()) * 1.3
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximately max_tokens, prioritizing the end."""
        tokens = self._count_tokens(text)
        if tokens <= max_tokens:
            return text
        
        # If too long, take the last portion (Discussion/Conclusion)
        # Rough estimate: 1 token ≈ 4 characters
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token
        
        if len(text) <= max_chars:
            return text
        
        # Take the last max_chars characters
        truncated = text[-max_chars:]
        logger.info(f"Truncated text from {len(text)} to {len(truncated)} chars (target: {max_tokens} tokens)")
        return truncated
    
    def download_and_parse(self, pdf_url: str) -> Optional[str]:
        """
        Download and parse PDF from URL.
        
        Args:
            pdf_url: URL to PDF file
        
        Returns:
            Extracted text or None if failed
        """
        try:
            logger.info(f"Downloading PDF from {pdf_url}")
            
            # Download PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse with PyMuPDF
            doc = fitz.open(stream=response.content, filetype="pdf")
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(text)
            
            doc.close()
            full_text = "\n\n".join(text_parts)
            
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(f"403 Forbidden error for {pdf_url}")
            else:
                logger.error(f"HTTP error downloading {pdf_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing PDF from {pdf_url}: {e}")
            return None
    
    def extract_limitations(self, paper: Paper, paper_text: Optional[str] = None, max_retries: int = 3) -> Optional[PaperAnalysis]:
        """
        Extract limitations from a paper using LLM.
        
        Args:
            paper: Paper object with metadata
            paper_text: Pre-extracted text (if None, will download and parse)
            max_retries: Maximum number of retries for API quota errors
        
        Returns:
            PaperAnalysis object or None if extraction failed
        """
        import time
        import re
        
        for attempt in range(max_retries):
            try:
                # Download and parse if text not provided
                if paper_text is None:
                    paper_text = self.download_and_parse(paper.pdf_url)
                    if paper_text is None:
                        logger.error(f"Failed to extract text from {paper.pdf_url}")
                        return None
                
                # Truncate to focus on Discussion/Conclusion (last 3000 tokens)
                truncated_text = self._truncate_to_tokens(paper_text, self.MAX_TOKENS)
                
                # Format prompt
                format_instructions = self.output_parser.get_format_instructions()
                
                messages = self.prompt.format_messages(
                    paper_title=paper.title,
                    paper_abstract=paper.abstract,
                    paper_text=truncated_text,
                    format_instructions=format_instructions
                )
                
                logger.info(f"Extracting limitations from paper: {paper.title[:50]}...")
                
                # Call LLM
                response = self.llm.invoke(messages)
                
                # Parse response
                if hasattr(response, 'content'):
                    content = response.content
                else:
                    content = str(response)
                
                # Try to extract JSON if wrapped in markdown code blocks
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
                
                # Try to parse as JSON
                try:
                    analysis = self.output_parser.parse(content)
                except Exception as parse_error:
                    logger.error(f"Failed to parse analysis response: {parse_error}")
                    logger.error(f"Response content: {content[:500]}...")
                    raise ValueError(f"Failed to parse LLM analysis response: {parse_error}")
                
                analysis.paper_title = paper.title
                analysis.paper_id = paper.arxiv_id
                
                logger.info(f"Extracted comprehensive analysis: "
                           f"{len(analysis.key_techniques)} techniques, "
                           f"{len(analysis.strengths)} strengths, "
                           f"{len(analysis.limitations)} limitations, "
                           f"{len(analysis.suggested_improvements)} improvements, "
                           f"{len(analysis.potential_solutions)} solutions")
                
                return analysis
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a quota/rate limit error
                if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        # Extract retry delay if available
                        retry_delay = 10
                        if "retry in" in error_str or "retry_delay" in error_str:
                            # Try to extract delay from error message
                            delay_match = re.search(r'(\d+\.?\d*)\s*s', error_str)
                            if delay_match:
                                retry_delay = float(delay_match.group(1)) + 2  # Add 2s buffer
                        
                        logger.warning(f"Quota/rate limit error (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Quota exceeded after {max_retries} attempts. Please check your API quota or use a different model.")
                        return None
                else:
                    # Non-quota error, log and return None
                    logger.error(f"Error extracting limitations from paper {paper.title}: {e}")
                    return None
        
        return None

