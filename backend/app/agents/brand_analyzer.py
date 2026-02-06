"""
PartnerScout AI - Brand Analyzer Agent (STORY-3.3.2)

AI agent that analyzes brand identity from description and reference Instagram profiles.
Extracts hashtags, keywords, visual themes, and generates embedding vectors for
semantic similarity matching.

Subtasks completed:
- SUB-3.3.2.1.1: Create app/agents/brand_analyzer.py
- SUB-3.3.2.1.2: Implement profile fetching via Apify
- SUB-3.3.2.1.3: Implement LLM chain for hashtag/keyword extraction
- SUB-3.3.2.1.4: Implement embedding generation
- SUB-3.3.2.1.5: Implement database storage in brand_dna table
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.agents.base import AgentResult, BaseAgent
from app.core.config import settings
from app.core.exceptions import AgentError, ApifyError, JobNotFoundError
from app.models.agent import BrandAnalyzerRequest, BrandAnalyzerResponse
from app.repositories.brand_repo import BrandRepository
from app.repositories.job_repo import JobRepository
from app.services.apify_service import ApifyService, get_apify_service
from app.services.llm_service import LLMService

# =============================================================================
# Logger Configuration
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Output Schema
# =============================================================================

class BrandAnalysisOutput(BaseModel):
    """Schema for LLM brand analysis output."""
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="Relevant hashtags with # prefix"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Brand keywords without # prefix"
    )
    visual_themes: List[str] = Field(
        default_factory=list,
        description="Identified visual themes and aesthetics"
    )
    content_pillars: List[str] = Field(
        default_factory=list,
        description="Main content pillars and topics"
    )
    target_audience_description: Optional[str] = Field(
        default=None,
        description="Description of target audience"
    )
    brand_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Brand DNA summary including voice, aesthetic, audience"
    )
    confidence_score: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Confidence score 0-100"
    )


# =============================================================================
# Brand Analyzer Agent
# =============================================================================

class BrandAnalyzerAgent(BaseAgent[BrandAnalyzerRequest, BrandAnalyzerResponse]):
    """
    AI agent for analyzing brand identity and extracting brand DNA.
    
    This agent:
    1. Fetches reference Instagram profiles via Apify
    2. Analyzes brand description and profile data with LLM
    3. Extracts hashtags, keywords, themes, and audience description
    4. Generates embedding vector for semantic similarity
    5. Stores brand DNA in the database
    
    Example:
        ```python
        agent = BrandAnalyzerAgent()
        request = BrandAnalyzerRequest(job_id=UUID("..."))
        response = await agent.run(request)
        print(response.hashtags)  # ["#sustainablefashion", "#ecofriendly", ...]
        ```
    """
    
    agent_name = "brand_analyzer"
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        apify_service: Optional[ApifyService] = None,
        job_repo: Optional[JobRepository] = None,
        brand_repo: Optional[BrandRepository] = None,
        **kwargs
    ):
        """
        Initialize the Brand Analyzer Agent.
        
        Args:
            llm_service: LLM service for text generation (optional)
            apify_service: Apify service for Instagram scraping (optional)
            job_repo: Job repository for accessing job data (optional)
            brand_repo: Brand repository for storing brand DNA (optional)
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(llm_service=llm_service, **kwargs)
        
        # Initialize services
        self._apify_service = apify_service or get_apify_service()
        self._job_repo = job_repo or JobRepository()
        self._brand_repo = brand_repo or BrandRepository()
        
        logger.debug(f"Initialized {self.agent_name} agent")
    
    # =========================================================================
    # Main Run Method (SUB-3.3.2.1.1)
    # =========================================================================
    
    async def run(self, input_data: BrandAnalyzerRequest) -> BrandAnalyzerResponse:
        """
        Execute brand analysis for a discovery job.
        
        This method:
        1. Fetches the job and validates it exists
        2. Scrapes reference Instagram profiles
        3. Analyzes brand with LLM to extract hashtags/keywords
        4. Generates embedding vector
        5. Stores brand DNA in database
        
        Args:
            input_data: BrandAnalyzerRequest containing job_id
            
        Returns:
            BrandAnalyzerResponse with extracted brand DNA
            
        Raises:
            AgentError: If analysis fails
            JobNotFoundError: If job doesn't exist
        """
        start_time = time.time()
        metrics = self._start_metrics()
        
        job_id = str(input_data.job_id)
        logger.info(f"Starting brand analysis for job: {job_id}")
        
        try:
            # Step 1: Fetch job data
            job = await self._fetch_job(job_id)
            brand_description = job.get("brand_description", "")
            reference_profiles = job.get("reference_profiles", [])
            
            if not reference_profiles:
                raise AgentError(
                    message="No reference profiles provided",
                    agent_name=self.agent_name,
                    details={"job_id": job_id}
                )
            
            # Step 2: Scrape reference profiles via Apify (SUB-3.3.2.1.2)
            profile_data, profiles_analyzed, posts_analyzed = await self._fetch_profiles(
                reference_profiles,
                max_posts=input_data.max_posts_per_profile
            )
            
            # Step 3: Analyze brand with LLM (SUB-3.3.2.1.3)
            analysis = await self._analyze_brand(brand_description, profile_data)
            
            # Step 4: Generate embedding (SUB-3.3.2.1.4)
            embedding_vector = await self._generate_embedding(
                brand_description,
                analysis
            )
            
            # Step 5: Store brand DNA in database (SUB-3.3.2.1.5)
            brand_dna = await self._store_brand_dna(
                job_id=job_id,
                analysis=analysis,
                embedding_vector=embedding_vector
            )
            
            # Calculate duration
            duration = time.time() - start_time
            self._complete_metrics(success=True)
            
            logger.info(
                f"Brand analysis completed for job {job_id}: "
                f"{len(analysis.hashtags)} hashtags, {len(analysis.keywords)} keywords, "
                f"duration={duration:.2f}s"
            )
            
            return BrandAnalyzerResponse(
                job_id=input_data.job_id,
                hashtags=analysis.hashtags,
                keywords=analysis.keywords,
                visual_themes=analysis.visual_themes,
                content_pillars=analysis.content_pillars,
                target_audience_description=analysis.target_audience_description,
                embedding_vector=embedding_vector,
                profiles_analyzed=profiles_analyzed,
                posts_analyzed=posts_analyzed,
                analysis_duration_seconds=duration,
            )
            
        except JobNotFoundError:
            raise
        except AgentError:
            raise
        except Exception as e:
            self._complete_metrics(success=False, error_message=str(e))
            logger.error(f"Brand analysis failed for job {job_id}: {e}")
            raise AgentError(
                message=f"Brand analysis failed: {str(e)}",
                agent_name=self.agent_name,
                details={"job_id": job_id, "error": str(e)}
            )
    
    # =========================================================================
    # Job Fetching
    # =========================================================================
    
    async def _fetch_job(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch job data from the database.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            Job data dictionary
            
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        logger.debug(f"Fetching job: {job_id}")
        return self._job_repo.get_by_id(job_id)
    
    # =========================================================================
    # Profile Fetching (SUB-3.3.2.1.2)
    # =========================================================================
    
    async def _fetch_profiles(
        self,
        profile_urls: List[str],
        max_posts: int = 20
    ) -> tuple[List[Dict[str, Any]], int, int]:
        """
        Fetch Instagram profile data via Apify.
        
        Args:
            profile_urls: List of Instagram profile URLs
            max_posts: Maximum posts to fetch per profile
            
        Returns:
            Tuple of (profile_data_list, profiles_analyzed_count, total_posts_analyzed)
        """
        logger.info(f"Fetching {len(profile_urls)} reference profiles via Apify")
        
        # Extract usernames from URLs
        usernames = []
        for url in profile_urls:
            username = self._apify_service.extract_username_from_url(url)
            if username:
                usernames.append(username)
            else:
                # Try using the URL as username directly
                username = url.strip().lstrip("@").split("/")[-1].strip()
                if username:
                    usernames.append(username)
        
        if not usernames:
            logger.warning("No valid usernames extracted from profile URLs")
            return [], 0, 0
        
        logger.debug(f"Extracted usernames: {usernames}")
        
        try:
            # Fetch profiles via Apify
            profiles = await self._apify_service.scrape_profiles(
                usernames=usernames,
                results_limit=max_posts
            )
            
            # Count posts analyzed
            total_posts = sum(
                len(p.get("recentPosts", [])) 
                for p in profiles
            )
            
            logger.info(
                f"Successfully fetched {len(profiles)} profiles, "
                f"{total_posts} posts analyzed"
            )
            
            return profiles, len(profiles), total_posts
            
        except ApifyError as e:
            logger.warning(f"Apify scraping failed: {e}, using empty profile data")
            return [], 0, 0
        except Exception as e:
            logger.warning(f"Profile fetching failed: {e}, using empty profile data")
            return [], 0, 0
    
    # =========================================================================
    # Brand Analysis with LLM (SUB-3.3.2.1.3)
    # =========================================================================
    
    async def _analyze_brand(
        self,
        brand_description: str,
        profile_data: List[Dict[str, Any]]
    ) -> BrandAnalysisOutput:
        """
        Analyze brand using LLM to extract hashtags, keywords, and themes.
        
        Args:
            brand_description: Brand description text
            profile_data: List of profile data from Apify
            
        Returns:
            BrandAnalysisOutput with extracted data
        """
        logger.debug("Analyzing brand with LLM")
        
        # Format profile data for the prompt
        profile_summary = self._format_profiles_for_prompt(profile_data)
        
        # Build the chain with JSON output parser
        chain = self.build_json_chain(pydantic_schema=BrandAnalysisOutput)
        
        # Prepare input variables
        input_vars = {
            "brand_description": brand_description,
            "reference_profiles": profile_summary,
        }
        
        try:
            # Invoke the chain
            result = await self.invoke_chain(chain, input_vars)
            
            # Parse result into BrandAnalysisOutput
            if isinstance(result, dict):
                analysis = BrandAnalysisOutput(**result)
            else:
                analysis = result
            
            # Normalize hashtags (ensure # prefix)
            analysis.hashtags = self._normalize_hashtags(analysis.hashtags)
            
            # Validate minimum requirements from config
            config = self._config.extra.get("output", {})
            min_hashtags = config.get("min_hashtags", 5)
            min_keywords = config.get("min_keywords", 5)
            
            if len(analysis.hashtags) < min_hashtags:
                logger.warning(
                    f"Only {len(analysis.hashtags)} hashtags extracted, "
                    f"minimum is {min_hashtags}"
                )
            
            if len(analysis.keywords) < min_keywords:
                logger.warning(
                    f"Only {len(analysis.keywords)} keywords extracted, "
                    f"minimum is {min_keywords}"
                )
            
            logger.debug(
                f"LLM analysis complete: {len(analysis.hashtags)} hashtags, "
                f"{len(analysis.keywords)} keywords"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Return empty analysis on failure
            return BrandAnalysisOutput(
                hashtags=[],
                keywords=[],
                visual_themes=[],
                content_pillars=[],
                confidence_score=0
            )
    
    def _format_profiles_for_prompt(
        self,
        profile_data: List[Dict[str, Any]]
    ) -> str:
        """
        Format profile data for inclusion in the LLM prompt.
        
        Args:
            profile_data: List of profile data dictionaries
            
        Returns:
            Formatted string for prompt
        """
        if not profile_data:
            return "No reference profiles available."
        
        formatted = []
        for i, profile in enumerate(profile_data, 1):
            username = profile.get("username", "unknown")
            full_name = profile.get("fullName", profile.get("full_name", ""))
            bio = profile.get("biography", "")
            followers = profile.get("followersCount", profile.get("followers_count", 0))
            
            # Extract hashtags from bio and recent posts
            hashtags = self._extract_hashtags_from_profile(profile)
            
            # Get recent post captions for content analysis
            captions = self._extract_post_captions(profile)
            
            profile_info = f"""
Profile {i}: @{username}
- Name: {full_name or 'N/A'}
- Followers: {followers:,}
- Bio: {bio or 'N/A'}
- Hashtags used: {', '.join(hashtags[:10]) if hashtags else 'N/A'}
- Recent content themes: {captions[:500] if captions else 'N/A'}
"""
            formatted.append(profile_info.strip())
        
        return "\n\n".join(formatted)
    
    def _extract_hashtags_from_profile(
        self,
        profile: Dict[str, Any]
    ) -> List[str]:
        """Extract hashtags from profile bio and posts."""
        hashtags = set()
        
        # From bio
        bio = profile.get("biography", "")
        if bio:
            import re
            bio_tags = re.findall(r"#\w+", bio)
            hashtags.update(bio_tags)
        
        # From recent posts
        posts = profile.get("recentPosts", [])
        for post in posts[:10]:  # Limit to 10 posts
            caption = post.get("caption", "") or ""
            import re
            post_tags = re.findall(r"#\w+", caption)
            hashtags.update(post_tags)
        
        return list(hashtags)
    
    def _extract_post_captions(
        self,
        profile: Dict[str, Any],
        max_length: int = 500
    ) -> str:
        """Extract concatenated post captions."""
        captions = []
        posts = profile.get("recentPosts", [])
        
        for post in posts[:5]:  # Limit to 5 posts
            caption = post.get("caption", "") or ""
            if caption:
                # Remove hashtags for cleaner text
                import re
                clean_caption = re.sub(r"#\w+", "", caption).strip()
                if clean_caption:
                    captions.append(clean_caption[:100])  # Limit each caption
        
        return " | ".join(captions)[:max_length]
    
    def _normalize_hashtags(self, hashtags: List[str]) -> List[str]:
        """Ensure all hashtags have # prefix and are lowercase."""
        normalized = []
        for tag in hashtags:
            tag = tag.strip()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            normalized.append(tag.lower())
        return list(set(normalized))  # Remove duplicates
    
    # =========================================================================
    # Embedding Generation (SUB-3.3.2.1.4)
    # =========================================================================
    
    async def _generate_embedding(
        self,
        brand_description: str,
        analysis: BrandAnalysisOutput
    ) -> Optional[List[float]]:
        """
        Generate embedding vector for brand DNA.
        
        Creates a combined text representation and generates
        an embedding using the configured provider (OpenAI or Gemini).
        
        Args:
            brand_description: Original brand description
            analysis: Analyzed brand data
            
        Returns:
            Embedding vector or None if generation fails
        """
        logger.debug(f"Generating embedding vector using provider: {settings.embedding_provider}")
        
        # Combine brand data for embedding
        embedding_text = self._create_embedding_text(brand_description, analysis)
        
        try:
            embeddings = self._get_embeddings_model()
            if embeddings is None:
                logger.warning("No embedding model available - check API keys")
                return None
            
            # Generate embedding
            vector = await embeddings.aembed_query(embedding_text)
            
            logger.debug(f"Generated embedding with {len(vector)} dimensions")
            return vector
            
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None
    
    def _get_embeddings_model(self):
        """
        Get the configured embeddings model based on EMBEDDING_PROVIDER setting.
        
        Returns:
            Embeddings instance (OpenAI or Gemini) or None if not configured
        """
        provider = settings.embedding_provider.lower()
        
        if provider == "openai":
            if not settings.openai.api_key:
                logger.warning("OpenAI API key not configured for embeddings")
                return None
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=settings.openai.api_key,
                model="text-embedding-ada-002"
            )
        
        elif provider == "gemini":
            if not settings.gemini.api_key:
                logger.warning("Gemini API key not configured for embeddings")
                return None
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                google_api_key=settings.gemini.api_key,
                model="models/embedding-001"
            )
        
        elif provider == "huggingface":
            if not settings.huggingface.api_key:
                logger.warning("HuggingFace API key not configured for embeddings")
                return None
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        else:
            logger.warning(f"Unknown embedding provider: {provider}")
            return None
    
    def _create_embedding_text(
        self,
        brand_description: str,
        analysis: BrandAnalysisOutput
    ) -> str:
        """
        Create text representation for embedding generation.
        
        Combines brand description, hashtags, keywords, and themes
        into a single text suitable for embedding.
        
        Args:
            brand_description: Original brand description
            analysis: Analyzed brand data
            
        Returns:
            Combined text for embedding
        """
        parts = [brand_description]
        
        if analysis.hashtags:
            parts.append("Hashtags: " + " ".join(analysis.hashtags[:10]))
        
        if analysis.keywords:
            parts.append("Keywords: " + ", ".join(analysis.keywords[:10]))
        
        if analysis.visual_themes:
            parts.append("Visual themes: " + ", ".join(analysis.visual_themes[:5]))
        
        if analysis.content_pillars:
            parts.append("Content pillars: " + ", ".join(analysis.content_pillars[:5]))
        
        if analysis.target_audience_description:
            parts.append("Target audience: " + analysis.target_audience_description[:200])
        
        return " | ".join(parts)
    
    # =========================================================================
    # Database Storage (SUB-3.3.2.1.5)
    # =========================================================================
    
    async def _store_brand_dna(
        self,
        job_id: str,
        analysis: BrandAnalysisOutput,
        embedding_vector: Optional[List[float]]
    ) -> Dict[str, Any]:
        """
        Store brand DNA in the database.
        
        Args:
            job_id: Job UUID string
            analysis: Analyzed brand data
            embedding_vector: Optional embedding vector
            
        Returns:
            Created brand DNA record
        """
        logger.debug(f"Storing brand DNA for job: {job_id}")
        
        # Check if brand DNA already exists for this job
        existing = self._brand_repo.get_by_job_id_optional(job_id)
        
        if existing:
            # Update existing record
            update_data = {
                "hashtags": analysis.hashtags,
                "keywords": analysis.keywords,
            }
            
            if analysis.visual_themes:
                update_data["visual_themes"] = analysis.visual_themes
            
            if analysis.content_pillars:
                update_data["content_pillars"] = analysis.content_pillars
            
            if analysis.target_audience_description:
                update_data["target_audience_description"] = analysis.target_audience_description
            
            if embedding_vector:
                update_data["embedding_vector"] = embedding_vector
            
            brand_dna = self._brand_repo.update_by_job_id(job_id, update_data)
            logger.info(f"Updated existing brand DNA for job: {job_id}")
        else:
            # Create new record
            brand_dna = self._brand_repo.create(
                job_id=job_id,
                hashtags=analysis.hashtags,
                keywords=analysis.keywords,
                visual_themes=analysis.visual_themes if analysis.visual_themes else None,
                content_pillars=analysis.content_pillars if analysis.content_pillars else None,
                target_audience_description=analysis.target_audience_description,
                embedding_vector=embedding_vector
            )
            logger.info(f"Created new brand DNA for job: {job_id}")
        
        return brand_dna
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    async def validate_input(self, input_data: BrandAnalyzerRequest) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input request data
            
        Returns:
            True if valid
            
        Raises:
            AgentError: If validation fails
        """
        if not input_data.job_id:
            raise AgentError(
                message="job_id is required",
                agent_name=self.agent_name,
                details={"field": "job_id"}
            )
        
        return True


# =============================================================================
# Factory Function
# =============================================================================

def get_brand_analyzer_agent(
    llm_service: Optional[LLMService] = None,
    apify_service: Optional[ApifyService] = None,
) -> BrandAnalyzerAgent:
    """
    Factory function to create a Brand Analyzer Agent.
    
    Args:
        llm_service: Optional custom LLM service
        apify_service: Optional custom Apify service
        
    Returns:
        BrandAnalyzerAgent instance
    """
    return BrandAnalyzerAgent(
        llm_service=llm_service,
        apify_service=apify_service,
    )
