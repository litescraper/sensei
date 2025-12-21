import arxiv
from datetime import datetime, timezone
from typing import List, Optional
import logging
from .models import Paper
from .config import ResearchDomain, DOMAIN_CATEGORIES, DOMAIN_QUERIES

logger = logging.getLogger(__name__)


class Harvester:
    """Fetches and filters papers from arxiv."""
    
    # Minimum publication date (2024-01-01)
    MIN_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
    
    def __init__(
        self,
        domain: ResearchDomain = ResearchDomain.AI_SAFETY,
        custom_queries: Optional[List[str]] = None,
        max_results_per_query: int = 20,
        min_citation_velocity: float = 5.0
    ):
        """
        Initialize the Harvester.
        
        Args:
            domain: Research domain to target
            custom_queries: Custom search queries (overrides domain defaults)
            max_results_per_query: Maximum results per query
            min_citation_velocity: Minimum citations per month (optional filter)
        """
        self.domain = domain
        self.max_results_per_query = max_results_per_query
        self.min_citation_velocity = min_citation_velocity
        
        # Get queries for domain
        if custom_queries:
            self.queries = custom_queries
        elif domain == ResearchDomain.CUSTOM:
            self.queries = []
        else:
            self.queries = DOMAIN_QUERIES.get(domain, [])
        
        # Get categories for domain
        self.categories = DOMAIN_CATEGORIES.get(domain, ["cs.LG", "cs.AI"])
    
    def search_arxiv(
        self,
        query: str,
        max_results: Optional[int] = None,
        categories: Optional[List[str]] = None
    ) -> List[Paper]:
        if max_results is None:
            max_results = self.max_results_per_query
        if categories is None:
            categories = self.categories
        
        papers = []
        
        try:
            # Build category filter
            category_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            full_query = f"({query}) AND ({category_filter})"
            
            logger.info(f"Searching arxiv with query: {full_query}")
            
            # Search arxiv
            search = arxiv.Search(
                query=full_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for result in search.results():
                try:
                    # Filter by date (must be 2024 or later)
                    if result.published < self.MIN_DATE:
                        logger.debug(f"Skipping paper {result.entry_id} - published before 2024")
                        continue
                    
                    # Extract paper data
                    # Handle categories - they can be strings or objects with .term
                    categories_list = []
                    for cat in result.categories:
                        if isinstance(cat, str):
                            categories_list.append(cat)
                        else:
                            categories_list.append(cat.term)
                    
                    # Handle authors - they can be strings or objects with .name
                    authors_list = []
                    for author in result.authors:
                        if isinstance(author, str):
                            authors_list.append(author)
                        else:
                            authors_list.append(author.name)
                    
                    paper = Paper(
                        title=result.title,
                        abstract=result.summary,
                        pdf_url=result.pdf_url,
                        published_date=result.published,
                        arxiv_id=result.entry_id.split('/')[-1],
                        authors=authors_list,
                        categories=categories_list
                    )
                    
                    papers.append(paper)
                    logger.debug(f"Added paper: {paper.title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"Error processing paper {result.entry_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching arxiv with query '{query}': {e}")
            raise
        
        logger.info(f"Found {len(papers)} papers matching query '{query}'")
        return papers
    
    def harvest_all(self) -> List[Paper]:
        all_papers = []
        seen_ids = set()
        
        if not self.queries:
            logger.warning(f"No queries defined for domain {self.domain}. Returning empty list.")
            return all_papers
        
        for query in self.queries:
            try:
                papers = self.search_arxiv(query)
                for paper in papers:
                    if paper.arxiv_id and paper.arxiv_id not in seen_ids:
                        seen_ids.add(paper.arxiv_id)
                        all_papers.append(paper)
            except Exception as e:
                logger.error(f"Failed to harvest papers for query '{query}': {e}")
                continue
        
        logger.info(f"Total unique papers harvested: {len(all_papers)}")
        return all_papers
    
    def filter_by_citation_velocity(self, papers: List[Paper]) -> List[Paper]:
        # This would require Semantic Scholar API integration
        # For now, return all papers
        # TODO: Implement citation velocity filtering if needed
        return papers

