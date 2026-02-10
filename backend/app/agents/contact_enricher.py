"""
PartnerScout AI - Contact Enricher Agent

Enriches profile contact information by scraping the profile's website
and extracting email, phone, and address using regex + LLM analysis.

This agent runs as Phase 4 in the orchestration pipeline, after scoring.
It uses httpx (free) for fetching and the existing LLM for extraction.
No additional API costs beyond the already-configured LLM provider.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.agents.base import AgentResult, BaseAgent
from app.core.exceptions import AgentError
from app.repositories.contact_repo import ContactRepository
from app.repositories.profile_repo import ProfileRepository
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# Pages most likely to contain contact info
CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/imprint",
    "/impressum",
    "/get-in-touch",
]

# Max content length to send to LLM (to avoid token limits)
MAX_CONTENT_LENGTH = 4000

# HTTP request settings
REQUEST_TIMEOUT = 10.0
MAX_PAGES_TO_FETCH = 3

# Regex patterns
EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
)

PHONE_PATTERN = re.compile(
    r'(?:\+?\d{1,4}[\s\-.]?)?\(?\d{1,4}\)?[\s\-.]?\d{1,4}[\s\-.]?\d{1,9}'
)

# Emails to ignore
IGNORE_EMAIL_DOMAINS = {
    "example.com", "test.com", "domain.com", "email.com",
    "sentry.io", "wixpress.com", "wordpress.com", "squarespace.com",
    "godaddy.com", "cloudflare.com", "instagram.com", "facebook.com",
    "google.com", "twitter.com", "tiktok.com",
}

IGNORE_EMAIL_PREFIXES = {
    "noreply", "no-reply", "donotreply", "abuse", "postmaster",
    "mailer-daemon", "webmaster", "hostmaster", "privacy",
    "security", "support@wix", "support@squarespace",
}

# Phone numbers to ignore (too short or common patterns)
MIN_PHONE_DIGITS = 7
MAX_PHONE_DIGITS = 15


# =============================================================================
# LLM Output Schema
# =============================================================================

class ContactExtractionOutput(BaseModel):
    """Schema for LLM contact extraction output."""

    email: Optional[str] = Field(
        default=None,
        description="Extracted email address"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Extracted phone number"
    )
    address: Optional[str] = Field(
        default=None,
        description="Extracted physical address"
    )
    email_confidence: Optional[str] = Field(
        default=None,
        description="Confidence level: high, medium, low"
    )
    phone_confidence: Optional[str] = Field(
        default=None,
        description="Confidence level: high, medium, low"
    )
    address_confidence: Optional[str] = Field(
        default=None,
        description="Confidence level: high, medium, low"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Where the info was found"
    )


# =============================================================================
# Request / Response Models
# =============================================================================

class ContactEnricherRequest(BaseModel):
    """Input for the Contact Enricher Agent."""

    profile_id: str
    job_id: str
    # Optional pre-fetched data to avoid extra DB calls
    profile_data: Optional[Dict[str, Any]] = None


class ContactEnricherResponse(BaseModel):
    """Output from the Contact Enricher Agent."""

    profile_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    email_source: Optional[str] = None
    sources_checked: int = 0
    enrichment_duration_seconds: float = 0.0


# =============================================================================
# Contact Enricher Agent
# =============================================================================

class ContactEnricherAgent(BaseAgent[ContactEnricherRequest, ContactEnricherResponse]):
    """
    Agent that enriches profile contact information by:
    1. Fetching the profile's website (external_url from Instagram)
    2. Crawling key pages (/contact, /about, etc.)
    3. Extracting emails, phones, addresses via regex
    4. Using LLM for intelligent structured extraction
    5. Storing results in profile_contacts table

    Cost: FREE (httpx requests) + minimal LLM usage (existing provider)
    """

    agent_name = "contact_enricher"

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        profile_repo: Optional[ProfileRepository] = None,
        contact_repo: Optional[ContactRepository] = None,
        **kwargs,
    ):
        super().__init__(llm_service=llm_service, **kwargs)
        self._profile_repo = profile_repo or ProfileRepository()
        self._contact_repo = contact_repo or ContactRepository()

    # =========================================================================
    # Main Run Method
    # =========================================================================

    async def run(self, input_data: ContactEnricherRequest) -> ContactEnricherResponse:
        """Execute contact enrichment for a profile."""
        start_time = time.time()
        metrics = self._start_metrics()
        profile_id = input_data.profile_id

        logger.info(f"Starting contact enrichment for profile: {profile_id}")

        try:
            # Step 1: Get profile data
            profile = input_data.profile_data or self._profile_repo.get_by_id(profile_id)
            username = profile.get("username", "unknown")
            full_name = profile.get("full_name", username)

            # Step 2: Determine website URL
            website_url = self._get_website_url(profile)
            if not website_url:
                logger.info(f"No website URL for @{username}, skipping enrichment")
                return ContactEnricherResponse(
                    profile_id=profile_id,
                    enrichment_duration_seconds=time.time() - start_time,
                )

            # Step 3: Fetch website pages
            pages = await self._fetch_website_pages(website_url)
            if not pages:
                logger.info(f"Could not fetch any pages for @{username} ({website_url})")
                return ContactEnricherResponse(
                    profile_id=profile_id,
                    website=website_url,
                    sources_checked=0,
                    enrichment_duration_seconds=time.time() - start_time,
                )

            # Step 4: Extract contacts via regex
            regex_contacts = self._extract_contacts_regex(pages)
            logger.info(
                f"Regex extraction for @{username}: "
                f"emails={len(regex_contacts['emails'])}, "
                f"phones={len(regex_contacts['phones'])}"
            )

            # Step 5: Use LLM for structured extraction (if regex didn't find enough)
            llm_contacts = None
            needs_llm = (
                not regex_contacts["emails"]
                or not regex_contacts["phones"]
            )
            if needs_llm:
                combined_text = self._prepare_text_for_llm(pages)
                if combined_text.strip():
                    llm_contacts = await self._llm_extract_contacts(
                        combined_text, username, full_name, website_url
                    )

            # Step 6: Merge results (regex + LLM)
            final = self._merge_results(regex_contacts, llm_contacts, profile)

            # Step 7: Store in database
            if final["email"] or final["phone"] or final["address"]:
                other_contacts = {}
                if final["address"]:
                    other_contacts["address"] = final["address"]

                self._contact_repo.upsert(
                    profile_id=profile_id,
                    email=final["email"],
                    email_source=final["email_source"],
                    phone=final["phone"],
                    website=website_url,
                    other_contacts=other_contacts if other_contacts else None,
                )
                logger.info(
                    f"Stored enriched contacts for @{username}: "
                    f"email={bool(final['email'])}, phone={bool(final['phone'])}, "
                    f"address={bool(final['address'])}"
                )

            duration = time.time() - start_time
            self._complete_metrics(success=True)

            return ContactEnricherResponse(
                profile_id=profile_id,
                email=final["email"],
                phone=final["phone"],
                address=final["address"],
                website=website_url,
                email_source=final["email_source"],
                sources_checked=len(pages),
                enrichment_duration_seconds=duration,
            )

        except Exception as e:
            self._complete_metrics(success=False, error_message=str(e))
            logger.error(f"Contact enrichment failed for {profile_id}: {e}")
            # Don't raise — enrichment failure shouldn't break the pipeline
            return ContactEnricherResponse(
                profile_id=profile_id,
                enrichment_duration_seconds=time.time() - start_time,
            )

    # =========================================================================
    # Website URL Resolution
    # =========================================================================

    def _get_website_url(self, profile: Dict[str, Any]) -> Optional[str]:
        """Extract and normalize the website URL from profile data."""
        url = (
            profile.get("external_url")
            or profile.get("website")
            or profile.get("contact_website")
        )
        if not url:
            return None

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Skip social media links (not useful for contact scraping)
        domain = urlparse(url).netloc.lower()
        skip_domains = {
            "instagram.com", "facebook.com", "twitter.com", "x.com",
            "tiktok.com", "youtube.com", "pinterest.com", "linkedin.com",
            "wa.me", "t.me", "bit.ly",
        }
        # Allow linktr.ee and bio.link — they often have contact info
        if any(d in domain for d in skip_domains):
            return None

        return url

    # =========================================================================
    # Website Fetching
    # =========================================================================

    async def _fetch_website_pages(
        self, base_url: str
    ) -> Dict[str, str]:
        """
        Fetch the main page and key subpages of a website.

        Returns:
            Dict mapping URL -> extracted text content
        """
        pages: Dict[str, str] = {}
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            verify=False,
        ) as client:
            # Fetch main page
            main_text = await self._fetch_single_page(client, base_url, headers)
            if main_text:
                pages[base_url] = main_text

            # Try contact-related subpages
            fetched = 1
            for path in CONTACT_PATHS:
                if fetched >= MAX_PAGES_TO_FETCH:
                    break
                sub_url = urljoin(base_url, path)
                if sub_url == base_url:
                    continue
                text = await self._fetch_single_page(client, sub_url, headers)
                if text:
                    pages[sub_url] = text
                    fetched += 1

        return pages

    async def _fetch_single_page(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
    ) -> Optional[str]:
        """Fetch a single page and extract text content."""
        try:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return None

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None

            html = response.text
            return self._extract_text_from_html(html)

        except (httpx.RequestError, httpx.HTTPStatusError, Exception) as e:
            logger.debug(f"Failed to fetch {url}: {type(e).__name__}: {e}")
            return None

    def _extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML, focusing on contact-relevant areas."""
        soup = BeautifulSoup(html, "lxml")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "noscript", "svg", "img"]):
            tag.decompose()

        # Extract structured data (JSON-LD) which often has business info
        structured_text = ""
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                import json
                data = json.loads(script.string or "")
                if isinstance(data, dict):
                    # Extract relevant fields
                    for key in ["email", "telephone", "phone", "address",
                                "streetAddress", "addressLocality",
                                "addressRegion", "postalCode", "contactPoint"]:
                        val = data.get(key)
                        if val:
                            structured_text += f" {key}: {val}"
                    # Check nested address
                    addr = data.get("address", {})
                    if isinstance(addr, dict):
                        for k, v in addr.items():
                            if v and isinstance(v, str):
                                structured_text += f" {k}: {v}"
            except (ValueError, TypeError):
                pass

        # Get main text
        text = soup.get_text(separator=" ", strip=True)

        # Combine structured data + page text
        full_text = structured_text + "\n" + text if structured_text else text

        # Trim to reasonable length
        return full_text[:8000]

    # =========================================================================
    # Regex Extraction
    # =========================================================================

    def _extract_contacts_regex(
        self, pages: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Extract contact info from all pages using regex patterns."""
        all_emails: List[str] = []
        all_phones: List[str] = []

        for url, text in pages.items():
            # Extract emails
            emails = EMAIL_PATTERN.findall(text)
            for email in emails:
                if self._is_valid_contact_email(email):
                    all_emails.append(email)

            # Extract phone numbers
            phones = PHONE_PATTERN.findall(text)
            for phone in phones:
                cleaned = self._clean_phone(phone)
                if cleaned:
                    all_phones.append(cleaned)

        # Deduplicate preserving order
        seen_emails = set()
        unique_emails = []
        for e in all_emails:
            lower = e.lower()
            if lower not in seen_emails:
                seen_emails.add(lower)
                unique_emails.append(e)

        seen_phones = set()
        unique_phones = []
        for p in all_phones:
            digits = re.sub(r'\D', '', p)
            if digits not in seen_phones:
                seen_phones.add(digits)
                unique_phones.append(p)

        return {
            "emails": unique_emails,
            "phones": unique_phones,
        }

    def _is_valid_contact_email(self, email: str) -> bool:
        """Check if an email is a valid contact (not spam/system)."""
        email_lower = email.lower()
        domain = email_lower.split("@")[-1]

        if domain in IGNORE_EMAIL_DOMAINS:
            return False

        local = email_lower.split("@")[0]
        for prefix in IGNORE_EMAIL_PREFIXES:
            if local.startswith(prefix):
                return False

        # Filter obvious non-emails
        if len(email) < 5 or len(email) > 254:
            return False

        return True

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Clean and validate a phone number."""
        # Count digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) < MIN_PHONE_DIGITS or len(digits) > MAX_PHONE_DIGITS:
            return None

        # Skip numbers that look like dates, IDs, or CSS values
        if re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}', phone):
            return None

        # Keep original formatting if it looks like a phone
        return phone.strip()

    # =========================================================================
    # LLM Extraction
    # =========================================================================

    def _prepare_text_for_llm(self, pages: Dict[str, str]) -> str:
        """Combine page texts for LLM, limited to MAX_CONTENT_LENGTH."""
        parts = []
        remaining = MAX_CONTENT_LENGTH

        for url, text in pages.items():
            if remaining <= 0:
                break
            chunk = text[:remaining]
            parts.append(f"[Page: {url}]\n{chunk}")
            remaining -= len(chunk)

        return "\n\n".join(parts)

    async def _llm_extract_contacts(
        self,
        page_content: str,
        username: str,
        full_name: str,
        website_url: str,
    ) -> Optional[ContactExtractionOutput]:
        """Use LLM to extract structured contact info from page content."""
        try:
            chain = self.build_json_chain(pydantic_schema=ContactExtractionOutput)

            input_vars = {
                "username": username,
                "full_name": full_name,
                "website_url": website_url,
                "page_content": page_content[:MAX_CONTENT_LENGTH],
            }

            result = await self.invoke_chain(chain, input_vars)

            if isinstance(result, dict):
                return ContactExtractionOutput(**result)
            return result

        except Exception as e:
            logger.warning(
                f"LLM contact extraction failed for @{username}: "
                f"{type(e).__name__}: {e}"
            )
            return None

    # =========================================================================
    # Result Merging
    # =========================================================================

    def _merge_results(
        self,
        regex_contacts: Dict[str, List[str]],
        llm_contacts: Optional[ContactExtractionOutput],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge regex and LLM extraction results, picking the best."""
        result = {
            "email": None,
            "phone": None,
            "address": None,
            "email_source": None,
        }

        # Priority for email:
        # 1. Existing business_email from Instagram
        # 2. Regex-extracted from website
        # 3. LLM-extracted
        # 4. Bio-extracted
        existing_email = profile.get("business_email")
        bio_email = self._extract_bio_email(profile.get("bio", "") or "")

        if existing_email and self._is_valid_contact_email(existing_email):
            result["email"] = existing_email
            result["email_source"] = "business_email"
        elif regex_contacts["emails"]:
            # Prefer contact/info/hello emails
            best = self._pick_best_email(regex_contacts["emails"])
            result["email"] = best
            result["email_source"] = "website"
        elif llm_contacts and llm_contacts.email and self._is_valid_contact_email(llm_contacts.email):
            result["email"] = llm_contacts.email
            result["email_source"] = "website"
        elif bio_email:
            result["email"] = bio_email
            result["email_source"] = "bio"

        # Priority for phone:
        # 1. Regex-extracted (more reliable)
        # 2. LLM-extracted
        if regex_contacts["phones"]:
            result["phone"] = regex_contacts["phones"][0]
        elif llm_contacts and llm_contacts.phone:
            result["phone"] = llm_contacts.phone

        # Address only from LLM (regex is unreliable for addresses)
        if llm_contacts and llm_contacts.address:
            result["address"] = llm_contacts.address

        return result

    def _pick_best_email(self, emails: List[str]) -> str:
        """Pick the most likely contact email from a list."""
        # Prefer emails with contact-related prefixes
        preferred_prefixes = [
            "contact", "hello", "info", "hi", "inquir",
            "collab", "partner", "business", "press",
        ]
        for email in emails:
            local = email.split("@")[0].lower()
            for prefix in preferred_prefixes:
                if prefix in local:
                    return email
        return emails[0]

    def _extract_bio_email(self, bio: str) -> Optional[str]:
        """Extract email from Instagram bio text."""
        emails = EMAIL_PATTERN.findall(bio)
        for email in emails:
            if self._is_valid_contact_email(email):
                return email
        return None

    # =========================================================================
    # Validation
    # =========================================================================

    async def validate_input(self, input_data: ContactEnricherRequest) -> bool:
        """Validate input data."""
        if not input_data.profile_id:
            raise AgentError(
                message="profile_id is required",
                agent_name=self.agent_name,
                details={"field": "profile_id"},
            )
        return True


# =============================================================================
# Factory Function
# =============================================================================

def get_contact_enricher_agent(
    llm_service: Optional[LLMService] = None,
) -> ContactEnricherAgent:
    """Factory function to create a Contact Enricher Agent."""
    return ContactEnricherAgent(llm_service=llm_service)
