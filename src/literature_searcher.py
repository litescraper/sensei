import os
import logging
from typing import List, Dict, Optional, Tuple
import arxiv
from serpapi import GoogleSearch
from semanticscholar import SemanticScholar
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class LiteraturePaper:
    def __init__(
        self,
        title: str,
        source: str,
        paper_id: Optional[str] = None,
        url: Optional[str] = None,
        relevance_reason: Optional[str] = None,
        year: Optional[int] = None
    ):
        self.title = title
        self.source = source  # "arxiv", "scholar", "semantic_scholar", "openreview"
        self.paper_id = paper_id
        self.url = url
        self.relevance_reason = relevance_reason
        self.year = year
    
    def __str__(self) -> str:
        paper_id_str = f"[{self.paper_id}]" if self.paper_id else "[No ID]"
        reason = f" - {self.relevance_reason}" if self.relevance_reason else ""  # Use regular dash, not em dash
        # Sanitize for JSON: remove newlines, escape quotes
        title = self.title.replace("\n", " ").replace("\r", " ").replace('"', "'")
        reason_clean = reason.replace("\n", " ").replace("\r", " ").replace('"', "'")
        return f"{paper_id_str} {title}{reason_clean}"


class LiteratureSearcher:
    """
    Implements Step 0 of the evaluation protocol: Literature quick-scan (grounding)
    """
    
    def __init__(
        self,
        serpapi_key: Optional[str] = None,
        semanticscholar_key: Optional[str] = None,
        web_search_provider: Optional[str] = None,
        serper_key: Optional[str] = None,
        serper_base_url: Optional[str] = None
    ):
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_API_KEY")
        self.semanticscholar_key = semanticscholar_key or os.getenv("SEMANTICSCHOLAR_API_KEY")
        self.web_search_provider = (
            web_search_provider or os.getenv("WEB_SEARCH_PROVIDER", "serpapi")
        ).lower()
        if self.web_search_provider not in ("serpapi", "serper"):
            raise ValueError("WEB_SEARCH_PROVIDER must be serpapi or serper")
        self.serper_key = serper_key or os.getenv("SERPER_API_KEY")
        self.serper_base_url = (
            serper_base_url or os.getenv("SERPER_BASE_URL") or "https://google.serper.dev"
        ).rstrip("/")
        
        if self.semanticscholar_key:
            self.s2_client = SemanticScholar(api_key=self.semanticscholar_key)
        else:
            self.s2_client = None
            logger.warning("Semantic Scholar API key not provided. Semantic Scholar search will be limited.")
    
    def search_arxiv(self, query: str, max_results: int = 10) -> List[LiteraturePaper]:
        papers = []
        try:
            logger.info(f"Searching arXiv with query: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for result in search.results():
                # Prefer recent papers
                year = result.published.year if result.published else None
                paper = LiteraturePaper(
                    title=result.title,
                    source="arxiv",
                    paper_id=result.entry_id.split('/')[-1],
                    url=result.pdf_url,
                    year=year
                )
                papers.append(paper)
        
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return papers
    
    def search_google_scholar(self, query: str, max_results: int = 10) -> List[LiteraturePaper]:
        papers = []
        
        if not self.serpapi_key:
            logger.warning("SerpAPI key not available. Skipping Google Scholar search.")
            return papers
        
        try:
            logger.info(f"Searching Google Scholar with query: {query}")
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google_scholar",
                "num": max_results
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            for result in organic_results:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                year = None
                if "publication_info" in result:
                    pub_info = result["publication_info"]
                    if "summary" in pub_info:
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', pub_info["summary"])
                        if year_match:
                            year = int(year_match.group())
                
                paper = LiteraturePaper(
                    title=title,
                    source="scholar",
                    url=link,
                    relevance_reason=snippet[:100] if snippet else None,
                    year=year
                )
                papers.append(paper)
        
        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
        
        return papers
    
    def search_semantic_scholar(self, query: str, max_results: int = 10) -> List[LiteraturePaper]:
        papers = []
        
        if not self.s2_client:
            logger.warning("Semantic Scholar client not available. Skipping Semantic Scholar search.")
            return papers
        
        try:
            logger.info(f"Searching Semantic Scholar with query: {query}")
            results = self.s2_client.search_paper(query, limit=max_results)
            
            for paper_data in results:
                title = paper_data.get("title", "")
                paper_id = paper_data.get("paperId", "")
                year = paper_data.get("year")
                url = paper_data.get("url", "")
                
                paper = LiteraturePaper(
                    title=title,
                    source="semantic_scholar",
                    paper_id=paper_id,
                    url=url,
                    year=year
                )
                papers.append(paper)
        
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
        
        return papers
    
    def search_openreview(self, query: str, max_results: int = 10) -> List[LiteraturePaper]:
        papers = []
        
        api_key = self.serper_key if self.web_search_provider == "serper" else self.serpapi_key
        if not api_key:
            logger.warning(
                "%s key not available. Skipping OpenReview search.", self.web_search_provider
            )
            return papers
        
        try:
            logger.info(f"Searching OpenReview with query: {query}")
            # Use Google search to find OpenReview papers
            search_query = f"{query} site:openreview.net"
            
            if self.web_search_provider == "serper":
                response = requests.post(
                    f"{self.serper_base_url}/search",
                    headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                    json={"q": search_query, "num": max(1, min(max_results, 10))},
                    timeout=30,
                )
                response.raise_for_status()
                organic_results = response.json().get("organic", [])
            else:
                params = {
                    "q": search_query,
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "num": max_results
                }

                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
            
            for result in organic_results:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                paper_id = None
                if "openreview.net/forum?id=" in link:
                    paper_id = link.split("id=")[-1].split("&")[0]
                
                paper = LiteraturePaper(
                    title=title,
                    source="openreview",
                    paper_id=paper_id,
                    url=link,
                    relevance_reason=snippet[:100] if snippet else None
                )
                papers.append(paper)
        
        except Exception as e:
            logger.error(f"Error searching OpenReview: {e}")
        
        return papers
    
    def comprehensive_search(
        self,
        idea_title: str,
        idea_keywords: List[str],
        max_results_per_source: int = 10
    ) -> Tuple[List[LiteraturePaper], str]:
        query = f"{idea_title} {' '.join(idea_keywords[:5])}"
        
        all_papers = []
        
        # Search all sources
        arxiv_papers = self.search_arxiv(query, max_results_per_source)
        all_papers.extend(arxiv_papers)
        
        scholar_papers = self.search_google_scholar(query, max_results_per_source)
        all_papers.extend(scholar_papers)
        
        semantic_papers = self.search_semantic_scholar(query, max_results_per_source)
        all_papers.extend(semantic_papers)
        
        openreview_papers = self.search_openreview(query, max_results_per_source)
        all_papers.extend(openreview_papers)
        
        # Sort by recency (prefer recent papers as per template)
        all_papers.sort(key=lambda p: p.year or 0, reverse=True)
        
        formatted_results = []
        seen_titles = set()
        
        for paper in all_papers:
            # Deduplicate by title
            title_lower = paper.title.lower()
            if title_lower in seen_titles:
                continue
            seen_titles.add(title_lower)
            
            paper_id_str = f"[{paper.paper_id}]" if paper.paper_id else "[No ID]"
            reason = paper.relevance_reason or "Relevant to research idea"
            # Limit reason to 15 words
            reason_words = reason.split()[:15]
            reason_short = " ".join(reason_words)
            
            formatted_line = f"{paper_id_str} {paper.title} – {reason_short}"
            formatted_results.append(formatted_line)
        
        formatted_text = "\n".join(formatted_results[:20])  # Limit to top 20
        
        logger.info(f"Found {len(all_papers)} total papers, {len(formatted_results)} unique")
        
        return all_papers, formatted_text

