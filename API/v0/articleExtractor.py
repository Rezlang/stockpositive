"""
ArticleExtractor - Smart web article content extraction using BeautifulSoup

This class fetches HTML from a webpage, removes scripts and styles,
and uses natural language processing heuristics to detect the main article content.

Supports multi-article pages like Yahoo Finance where a main article is followed
by related articles, and handles "show more" hidden content.
"""

import requests
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import urljoin, urlparse
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
import math


@dataclass
class ArticleContent:
    """Data class to hold extracted article content"""
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    content: Optional[str] = None
    paragraphs: List[str] = field(default_factory=list)
    main_image: Optional[str] = None
    is_primary: bool = True  # True if this is the main article on the page


@dataclass
class PageExtractionResult:
    """Result containing all articles extracted from a page"""
    url: str
    articles: List[ArticleContent] = field(default_factory=list)
    related_article_links: List[Dict[str, str]] = field(
        default_factory=list)  # Links to lazy-loaded articles

    @property
    def primary_article(self) -> Optional[ArticleContent]:
        """Get the primary/main article from the page"""
        for article in self.articles:
            if article.is_primary:
                return article
        return self.articles[0] if self.articles else None


class ArticleExtractor:
    """
    A BeautifulSoup-based class for extracting article content from webpages.

    Features:
    - Extracts multiple articles from a single page
    - Handles hidden "show more" content
    - Uses text/link density analysis for smart content detection
    - Supports Yahoo Finance and other news sites
    """

    # Tags to completely remove (they contain no useful content)
    REMOVE_TAGS = [
        'script', 'style', 'noscript', 'iframe', 'svg', 'canvas',
        'video', 'audio', 'form', 'input', 'button', 'select', 'textarea',
        'nav', 'footer', 'header', 'aside', 'advertisement', 'figcaption'
    ]

    # Common class/id patterns that indicate main content
    CONTENT_PATTERNS = [
        r'article[-_]?(body|content|text|main)?',
        r'(post|entry|blog)[-_]?(body|content|text)?',
        r'(story|news)[-_]?(body|content|text)?',
        r'main[-_]?(content|body|text|article)?',
        r'content[-_]?(body|main|article|text)?',
        r'body[-_]?(content|text|article)?',
        r'caas[-_]?body',  # Yahoo specific
        r'article-body',
        r'story-body',
    ]

    # Patterns that indicate non-content areas
    NOISE_PATTERNS = [
        r'sidebar', r'side[-_]?bar', r'widget', r'comment', r'footer',
        r'header', r'nav', r'menu', r'breadcrumb', r'share', r'social',
        r'related', r'recommend', r'popular', r'trending', r'subscribe',
        r'newsletter', r'advertisement', r'ad[-_]?', r'promo', r'sponsor',
        r'banner', r'modal', r'popup', r'overlay', r'cookie', r'consent'
    ]

    # Common author patterns
    AUTHOR_PATTERNS = [
        r'author', r'byline', r'writer', r'contributor', r'correspondent'
    ]

    # Common date patterns
    DATE_PATTERNS = [
        r'date', r'time', r'publish', r'posted', r'updated', r'modified'
    ]

    # Default headers that mimic a real browser
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    def __init__(self, user_agent: str = None, headers: Dict[str, str] = None):
        """
        Initialize the ArticleExtractor.

        Args:
            user_agent: Custom user agent string for requests (overrides default)
            headers: Custom headers dict to merge with defaults
        """
        self.session = requests.Session()

        # Start with default headers
        self.session.headers.update(self.DEFAULT_HEADERS)

        # Override user agent if provided
        if user_agent:
            self.session.headers['User-Agent'] = user_agent

        # Merge any custom headers
        if headers:
            self.session.headers.update(headers)

    def fetch_html(self, url: str, timeout: int = 15) -> str:
        """
        Fetch HTML content from a URL.

        Args:
            url: The webpage URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Raw HTML string
        """
        import time

        # Extract domain for Referer header
        parsed = urlparse(url)
        referer = f"{parsed.scheme}://{parsed.netloc}/"

        # Set per-request headers - don't send Accept-Encoding to get uncompressed response
        request_headers = {
            'Referer': referer,
            'Host': parsed.netloc,
            'Accept-Encoding': 'identity',  # Request uncompressed content
        }

        # Some sites need cookies from an initial request
        # First, try to get the homepage to establish cookies
        try:
            self.session.get(
                f"{parsed.scheme}://{parsed.netloc}/",
                timeout=5,
                headers={'Accept-Encoding': 'identity'}
            )
            time.sleep(0.5)  # Small delay to appear more human-like
        except Exception:
            pass  # Ignore errors on cookie fetch

        response = self.session.get(
            url,
            timeout=timeout,
            headers=request_headers,
            allow_redirects=True
        )
        response.raise_for_status()

        # Handle encoding properly
        # First try to get encoding from response headers
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            # Try to detect from content
            response.encoding = response.apparent_encoding

        return response.text

    def _unhide_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Remove display:none styles to reveal hidden content (like "show more" sections).
        This must be called BEFORE clean_html which removes hidden elements.

        Args:
            soup: BeautifulSoup object

        Returns:
            BeautifulSoup with hidden content revealed
        """
        # Yahoo Finance specific: find read-more-wrapper and unhide it
        for wrapper in soup.find_all(class_=re.compile(r'read[-_]?more[-_]?wrapper', re.I)):
            if wrapper.get('style'):
                # Remove display:none from style
                wrapper['style'] = re.sub(
                    r'display\s*:\s*none\s*;?', '', wrapper['style'], flags=re.I)

        # Generic: find elements with "more" or "expand" in class that have display:none
        for elem in soup.find_all(style=re.compile(r'display\s*:\s*none', re.I)):
            classes = ' '.join(elem.get('class', []))
            # If it looks like hidden article content, unhide it
            if re.search(r'(more|expand|continue|full|rest)', classes, re.I):
                elem['style'] = re.sub(
                    r'display\s*:\s*none\s*;?', '', elem['style'], flags=re.I)
            # Also unhide if parent looks like article body
            parent = elem.parent
            if parent:
                parent_classes = ' '.join(parent.get('class', []))
                if re.search(r'(body|content|article|story)', parent_classes, re.I):
                    elem['style'] = re.sub(
                        r'display\s*:\s*none\s*;?', '', elem['style'], flags=re.I)

        return soup

    def clean_html(self, soup: BeautifulSoup, print_cleaned: bool = False) -> BeautifulSoup:
        """
        Remove scripts, styles, and other non-content elements from the HTML.

        Args:
            soup: BeautifulSoup object
            print_cleaned: If True, print the cleaned HTML

        Returns:
            Cleaned BeautifulSoup object
        """
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove unwanted tags
        for tag in self.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove elements with hidden styles (but NOT read-more content we've unhidden)
        for element in soup.find_all(style=re.compile(r'display\s*:\s*none|visibility\s*:\s*hidden', re.I)):
            # Don't remove if it's part of the article body structure
            classes = ' '.join(element.get('class', []))
            if not re.search(r'(more|wrapper|body|content)', classes, re.I):
                element.decompose()

        # Remove elements with aria-hidden="true"
        for element in soup.find_all(attrs={'aria-hidden': 'true'}):
            element.decompose()

        if print_cleaned:
            print("\n" + "=" * 80)
            print("CLEANED HTML (scripts and styles removed)")
            print("=" * 80)
            # Pretty print with limited length for readability
            cleaned_html = soup.prettify()
            if len(cleaned_html) > 10000:
                print(cleaned_html[:10000])
                print(
                    f"\n... [truncated, total {len(cleaned_html)} characters]")
            else:
                print(cleaned_html)
            print("=" * 80 + "\n")

        return soup

    def _matches_pattern(self, value: str, patterns: List[str]) -> bool:
        """Check if a value matches any of the given regex patterns."""
        if not value:
            return False
        value_lower = value.lower()
        return any(re.search(pattern, value_lower) for pattern in patterns)

    def _get_element_identifier(self, element) -> str:
        """Get combined class and id string for pattern matching."""
        classes = ' '.join(element.get('class', []))
        element_id = element.get('id', '')
        return f"{classes} {element_id}".strip()

    def _calculate_text_density(self, element) -> float:
        """
        Calculate text density (text length / tag count).
        Higher density = more likely to be content.
        """
        text = element.get_text(strip=True)
        tag_count = len(element.find_all()) + 1
        return len(text) / tag_count if tag_count > 0 else 0

    def _calculate_link_density(self, element) -> float:
        """
        Calculate link density (link text length / total text length).
        Lower density = more likely to be content (ads have lots of links).
        """
        text = element.get_text(strip=True)
        if not text:
            return 1.0

        link_text = ''
        for link in element.find_all('a'):
            link_text += link.get_text(strip=True)

        return len(link_text) / len(text)

    def _score_element(self, element) -> float:
        """
        Score an element based on multiple heuristics to determine
        if it's likely to contain the main article content.

        Returns a score where higher = more likely to be main content.
        """
        score = 0.0
        identifier = self._get_element_identifier(element)

        # Bonus for semantic article tags
        if element.name == 'article':
            score += 50
        elif element.name == 'main':
            score += 40
        elif element.name in ['section', 'div']:
            score += 5

        # Bonus for content-related class/id patterns
        if self._matches_pattern(identifier, self.CONTENT_PATTERNS):
            score += 40

        # Penalty for noise patterns
        if self._matches_pattern(identifier, self.NOISE_PATTERNS):
            score -= 50

        # Text density scoring
        text_density = self._calculate_text_density(element)
        score += min(text_density / 10, 20)  # Cap bonus at 20

        # Link density penalty (high link density = probably navigation/ads)
        link_density = self._calculate_link_density(element)
        if link_density > 0.5:
            score -= 30
        elif link_density > 0.3:
            score -= 15

        # Paragraph count bonus
        paragraphs = element.find_all('p')
        meaningful_paragraphs = [
            p for p in paragraphs if len(p.get_text(strip=True)) > 50]
        score += len(meaningful_paragraphs) * 5

        # Word count in paragraphs
        total_words = sum(len(p.get_text().split()) for p in paragraphs)
        score += math.log(total_words + 1) * 3

        return score

    def _find_content_candidates(self, soup: BeautifulSoup) -> List[Tuple[float, any]]:
        """
        Find and score all potential content container elements.

        Returns:
            List of (score, element) tuples, sorted by score descending
        """
        candidates = []

        # First, look for semantic HTML5 article elements
        for article in soup.find_all('article'):
            score = self._score_element(article)
            candidates.append((score, article))

        # Look for main tag
        for main in soup.find_all('main'):
            score = self._score_element(main)
            candidates.append((score, main))

        # Look for divs/sections with content-related classes
        for element in soup.find_all(['div', 'section']):
            identifier = self._get_element_identifier(element)
            if self._matches_pattern(identifier, self.CONTENT_PATTERNS):
                score = self._score_element(element)
                candidates.append((score, element))

        # If no good candidates, fall back to scoring all major containers
        if not candidates or max(c[0] for c in candidates) < 20:
            for element in soup.find_all(['div', 'section', 'article', 'main']):
                if element not in [c[1] for c in candidates]:
                    # Only consider elements with substantial content
                    if len(element.get_text(strip=True)) > 200:
                        score = self._score_element(element)
                        candidates.append((score, element))

        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates

    def _extract_title(self, soup: BeautifulSoup, container=None) -> Optional[str]:
        """Extract the article title using multiple strategies."""
        search_area = container or soup

        # If we have a container, look for h1/h2/h3 within it first
        if container:
            for tag in ['h1', 'h2', 'h3']:
                h = container.find(tag)
                if h:
                    return h.get_text(strip=True)

        # Try og:title meta tag (most reliable for page-level)
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        # Try h1 tags
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Try title tag (often has site name appended)
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Try to remove common site name patterns
            for sep in [' | ', ' - ', ' :: ', ' // ']:
                if sep in title:
                    parts = title.split(sep)
                    # Usually the article title is the longest part
                    return max(parts, key=len).strip()
            return title

        return None

    def _clean_author_text(self, text: str) -> Optional[str]:
        """Clean and extract just the author name from text that may contain roles/titles."""
        if not text:
            return None

        # Remove common prefixes
        text = re.sub(r'^(by|written by|author:?)\s*', '', text, flags=re.I)

        # Remove common role/title suffixes that get concatenated
        # Pattern matches: "Name" followed by role words
        role_patterns = [
            r'(Associate|Senior|Staff|Managing|Executive|Contributing|Assistant)?\s*'
            r'(News\s*)?(Editor|Writer|Reporter|Correspondent|Journalist|Contributor|Author|Columnist)',
            r'(News\s*)?Editor[\s-]*(in[\s-]*Chief)?',
            r'is a .+$',  # "is a Trust Project member" etc.
            r',\s*(a\s+)?(staff|senior|associate).*$',
        ]

        for pattern in role_patterns:
            text = re.sub(pattern, '', text, flags=re.I)

        # Clean up any trailing/leading whitespace and punctuation
        text = re.sub(r'[\s,\-]+$', '', text)
        text = re.sub(r'^[\s,\-]+', '', text)

        return text.strip() if text else None

    def _get_innermost_author_name(self, element) -> Optional[str]:
        """
        Find the innermost element containing 'name' in class/attr,
        or the first link/span with just a name.
        """
        # First, look for elements with 'name' in class or data attributes
        name_elem = element.find(class_=re.compile(r'name', re.I))
        if name_elem:
            text = name_elem.get_text(strip=True)
            if text and len(text) < 80:
                return self._clean_author_text(text)

        # Look for itemprop="name"
        name_elem = element.find(attrs={'itemprop': 'name'})
        if name_elem:
            text = name_elem.get_text(strip=True)
            if text and len(text) < 80:
                return self._clean_author_text(text)

        # Look for a link that's likely the author name (short text, no role words)
        for link in element.find_all('a'):
            text = link.get_text(strip=True)
            # Author names are typically 2-4 words, no role keywords
            if text and len(text) < 50:
                word_count = len(text.split())
                if 1 <= word_count <= 5:
                    # Check if it doesn't contain role words
                    if not re.search(r'(editor|writer|reporter|correspondent|journalist|contributor|columnist)', text, re.I):
                        return self._clean_author_text(text)

        # Fallback: get direct text content, not from children
        # This handles cases where the author name is direct text
        direct_text = ''
        for child in element.children:
            if isinstance(child, NavigableString):
                direct_text += str(child)
        direct_text = direct_text.strip()
        if direct_text and len(direct_text) < 50:
            cleaned = self._clean_author_text(direct_text)
            if cleaned and len(cleaned.split()) <= 5:
                return cleaned

        return None

    def _extract_author(self, soup: BeautifulSoup, container=None) -> Optional[str]:
        """Extract the article author."""
        search_area = container or soup

        # Try meta tags first (most reliable)
        for meta_name in ['author', 'article:author', 'twitter:creator']:
            meta = soup.find('meta', attrs={'name': meta_name}) or soup.find(
                'meta', property=meta_name)
            if meta and meta.get('content'):
                return self._clean_author_text(meta['content'])

        # Try schema.org author with name
        author_elem = search_area.find(attrs={'itemprop': 'author'})
        if author_elem:
            name_elem = author_elem.find(attrs={'itemprop': 'name'})
            if name_elem:
                return self._clean_author_text(name_elem.get_text(strip=True))
            # Try to get innermost name
            inner_name = self._get_innermost_author_name(author_elem)
            if inner_name:
                return inner_name

        # Try data attributes that indicate author name specifically
        for attr_pattern in ['data-cy-id', 'data-testid', 'data-test', 'data-author']:
            # First look for author-name specifically
            for element in search_area.find_all(attrs={attr_pattern: re.compile(r'author[-_]?name', re.I)}):
                text = element.get_text(strip=True)
                if text and len(text) < 80:
                    return self._clean_author_text(text)
            # Then look for author more broadly
            for element in search_area.find_all(attrs={attr_pattern: re.compile(r'author', re.I)}):
                # Try to find innermost name first
                inner_name = self._get_innermost_author_name(element)
                if inner_name:
                    return inner_name
                # Fallback to full text if short enough
                text = element.get_text(strip=True)
                if text and len(text) < 50:
                    return self._clean_author_text(text)

        # Try elements with 'author-name' or 'authorName' class specifically
        for element in search_area.find_all(class_=re.compile(r'author[-_]?name', re.I)):
            text = element.get_text(strip=True)
            if text and len(text) < 80:
                return self._clean_author_text(text)

        # Try common author/byline class patterns
        for element in search_area.find_all(['span', 'div', 'a', 'p']):
            identifier = self._get_element_identifier(element)
            if self._matches_pattern(identifier, self.AUTHOR_PATTERNS):
                # Try to get innermost name element
                inner_name = self._get_innermost_author_name(element)
                if inner_name:
                    return inner_name
                # Fallback: if text is short and looks like a name
                text = element.get_text(strip=True)
                if text and len(text) < 50:
                    cleaned = self._clean_author_text(text)
                    if cleaned and len(cleaned.split()) <= 5:
                        return cleaned

        # Try rel="author" links
        author_link = search_area.find('a', rel='author')
        if author_link:
            text = author_link.get_text(strip=True)
            if text and len(text) < 80:
                return self._clean_author_text(text)

        return None

    def _extract_date(self, soup: BeautifulSoup, container=None) -> Optional[str]:
        """Extract the article publish date."""
        search_area = container or soup

        # Try time element with datetime attribute
        time_elem = search_area.find('time', datetime=True)
        if time_elem:
            return time_elem['datetime']

        # Try meta tags
        for meta_name in ['article:published_time', 'datePublished', 'date', 'pubdate']:
            meta = soup.find('meta', attrs={'name': meta_name}) or soup.find(
                'meta', property=meta_name)
            if meta and meta.get('content'):
                return meta['content'].strip()

        # Try schema.org date
        for prop in ['datePublished', 'dateCreated']:
            date_elem = search_area.find(attrs={'itemprop': prop})
            if date_elem:
                if date_elem.get('datetime'):
                    return date_elem['datetime']
                if date_elem.get('content'):
                    return date_elem['content']
                return date_elem.get_text(strip=True)

        return None

    def _extract_main_image(self, soup: BeautifulSoup, base_url: str, container=None) -> Optional[str]:
        """Extract the main article image URL."""
        # Try og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return urljoin(base_url, og_image['content'])

        # Try twitter:image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return urljoin(base_url, twitter_image['content'])

        # Look for large images in container
        if container:
            for img in container.find_all('img', src=True):
                src = img.get('src', '')
                # Skip small images, icons, tracking pixels
                width = img.get('width', '')
                height = img.get('height', '')
                if (width and int(width) < 100) or (height and int(height) < 100):
                    continue
                if 'icon' in src.lower() or 'logo' in src.lower() or 'pixel' in src.lower():
                    continue
                return urljoin(base_url, src)

        return None

    def _extract_paragraphs(self, content_element, include_hidden: bool = True) -> List[str]:
        """
        Extract meaningful paragraphs from the content element.

        Args:
            content_element: BeautifulSoup element containing article content
            include_hidden: If True, also extract from previously hidden sections
        """
        paragraphs = []
        seen_texts = set()  # Avoid duplicates

        # Find all paragraph-like elements including in hidden sections
        for p in content_element.find_all(['p', 'h2', 'h3', 'blockquote']):
            text = p.get_text(strip=True)

            # Filter out very short paragraphs and common non-content
            if len(text) > 30 and text not in seen_texts:
                # Skip if it looks like a caption or attribution
                if not re.match(r'^(photo|image|credit|source|getty|reuters|ap|afp):', text, re.I):
                    # Skip promotional/boilerplate content
                    if not re.search(r'(stock advisor|motley fool|subscribe|sign up for)', text, re.I):
                        paragraphs.append(text)
                        seen_texts.add(text)

        return paragraphs

    def _extract_yahoo_articles(self, soup: BeautifulSoup, url: str) -> PageExtractionResult:
        """
        Yahoo Finance-specific extraction that handles their page structure.

        Args:
            soup: BeautifulSoup object (already cleaned)
            url: Original page URL

        Returns:
            PageExtractionResult with all articles found
        """
        result = PageExtractionResult(url=url)

        # Find the main article wrapper
        main_article_wrap = soup.find(
            'article', class_=re.compile(r'article[-_]?wrap', re.I))

        if main_article_wrap:
            # Extract main article
            main_article = ArticleContent(
                url=url,
                is_primary=True,
                title=self._extract_title(soup, main_article_wrap),
                author=self._extract_author(soup, main_article_wrap),
                publish_date=self._extract_date(soup, main_article_wrap),
                main_image=self._extract_main_image(
                    soup, url, main_article_wrap)
            )

            # Find body content - Yahoo uses class="body"
            body = main_article_wrap.find(class_=re.compile(r'^body$|^body\s'))
            if body:
                # Get paragraphs from visible content
                main_article.paragraphs = self._extract_paragraphs(body)

                # Also look for read-more-wrapper content that we've unhidden
                read_more = body.find(class_=re.compile(
                    r'read[-_]?more[-_]?wrapper', re.I))
                if read_more:
                    more_paragraphs = self._extract_paragraphs(read_more)
                    # Add only new paragraphs
                    existing_texts = set(main_article.paragraphs)
                    for p in more_paragraphs:
                        if p not in existing_texts:
                            main_article.paragraphs.append(p)

                main_article.content = '\n\n'.join(main_article.paragraphs)

            result.articles.append(main_article)

        # Find related content stream articles
        related_stream = soup.find(class_=re.compile(
            r'related[-_]?content[-_]?stream', re.I))
        if related_stream:
            # Look for article containers in the stream
            article_containers = related_stream.find_all(
                class_=re.compile(r'loader[-_]?container|article', re.I),
                recursive=True
            )

            for container in article_containers:
                # Check if this container has actual loaded content
                article_div = container.find(
                    class_=re.compile(r'^article\s|^article$', re.I))
                if article_div:
                    # Get body content
                    body = article_div.find(
                        class_=re.compile(r'^body$|^body\s'))
                    if body:
                        paragraphs = self._extract_paragraphs(body)
                        if paragraphs:
                            # This is a loaded article
                            article = ArticleContent(
                                url=url,  # Same page
                                is_primary=False,
                                title=self._extract_title(soup, article_div),
                                paragraphs=paragraphs,
                                content='\n\n'.join(paragraphs)
                            )

                            # Avoid duplicates
                            if not any(a.content == article.content for a in result.articles):
                                result.articles.append(article)

                # Check for lazy-loaded article links (not yet loaded)
                links = container.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if '/news/' in href or '/article/' in href:
                        full_url = urljoin(url, href)
                        title_elem = link.find(['h2', 'h3', 'h4'])
                        title = title_elem.get_text(
                            strip=True) if title_elem else link.get_text(strip=True)

                        if title and len(title) > 10:
                            # Check if we don't already have this article
                            if not any(full_url == a.url for a in result.articles):
                                if not any(full_url == r['url'] for r in result.related_article_links):
                                    result.related_article_links.append({
                                        'url': full_url,
                                        'title': title
                                    })

        return result

    def _is_yahoo_finance(self, url: str, soup: BeautifulSoup) -> bool:
        """Check if this is a Yahoo Finance page."""
        if 'yahoo.com' in url.lower():
            return True
        # Also check for Yahoo-specific classes
        return soup.find(class_=re.compile(r'yf-|caas-', re.I)) is not None

    def extract_all(self, url: str, print_cleaned_html: bool = True) -> PageExtractionResult:
        """
        Extract all articles from a URL (main article + related articles).

        Args:
            url: The webpage URL to extract content from
            print_cleaned_html: If True, print HTML after removing scripts/styles

        Returns:
            PageExtractionResult containing all extracted articles
        """
        # Fetch HTML
        html = self.fetch_html(url)

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Unhide content BEFORE cleaning (reveal "show more" sections)
        soup = self._unhide_content(soup)

        # Clean HTML (removes scripts, styles, etc.)
        soup = self.clean_html(soup, print_cleaned=print_cleaned_html)

        # Use site-specific extraction if available
        if self._is_yahoo_finance(url, soup):
            return self._extract_yahoo_articles(soup, url)

        # Generic extraction for other sites
        return self._extract_generic(soup, url)

    def _extract_generic(self, soup: BeautifulSoup, url: str) -> PageExtractionResult:
        """Generic extraction for non-Yahoo sites."""
        result = PageExtractionResult(url=url)

        # Find all article elements on the page
        article_elements = soup.find_all('article')

        if article_elements:
            for i, article_elem in enumerate(article_elements):
                article = ArticleContent(
                    url=url,
                    is_primary=(i == 0),
                    title=self._extract_title(
                        soup if i == 0 else article_elem, article_elem),
                    author=self._extract_author(
                        soup if i == 0 else article_elem, article_elem),
                    publish_date=self._extract_date(
                        soup if i == 0 else article_elem, article_elem),
                    main_image=self._extract_main_image(
                        soup, url, article_elem) if i == 0 else None
                )

                article.paragraphs = self._extract_paragraphs(article_elem)
                if article.paragraphs:
                    article.content = '\n\n'.join(article.paragraphs)
                    result.articles.append(article)

        # If no articles found, use heuristic scoring
        if not result.articles:
            candidates = self._find_content_candidates(soup)
            if candidates:
                best_score, best_element = candidates[0]
                print(f"\nBest content candidate score: {best_score:.1f}")
                print(
                    f"Element: <{best_element.name}> with classes: {best_element.get('class', [])}")

                article = ArticleContent(
                    url=url,
                    is_primary=True,
                    title=self._extract_title(soup),
                    author=self._extract_author(soup),
                    publish_date=self._extract_date(soup),
                    main_image=self._extract_main_image(soup, url)
                )
                article.paragraphs = self._extract_paragraphs(best_element)
                article.content = '\n\n'.join(article.paragraphs)
                result.articles.append(article)

        return result

    def extract(self, url: str, print_cleaned_html: bool = True) -> ArticleContent:
        """
        Extract the primary article content from a URL.
        For multi-article extraction, use extract_all() instead.

        Args:
            url: The webpage URL to extract content from
            print_cleaned_html: If True, print HTML after removing scripts/styles

        Returns:
            ArticleContent object with extracted data
        """
        result = self.extract_all(url, print_cleaned_html)
        return result.primary_article or ArticleContent(url=url)

    def extract_from_html(self, html: str, url: str = '', print_cleaned_html: bool = True) -> PageExtractionResult:
        """
        Extract all articles from raw HTML string.

        Args:
            html: Raw HTML string
            url: Optional URL for resolving relative links
            print_cleaned_html: If True, print HTML after removing scripts/styles

        Returns:
            PageExtractionResult with all extracted articles
        """
        soup = BeautifulSoup(html, 'html.parser')
        soup = self._unhide_content(soup)
        soup = self.clean_html(soup, print_cleaned=print_cleaned_html)

        if self._is_yahoo_finance(url, soup):
            return self._extract_yahoo_articles(soup, url)

        return self._extract_generic(soup, url)


# Example usage and testing
if __name__ == '__main__':
    import sys

    # Default test URL
    test_url = 'https://simplywall.st/stocks/us/semiconductors/nasdaq-nvda/nvidia/news/nvidia-nvda-evaluating-the-stocks-valuation-as-ces-2026-ai-a'

    # Allow URL from command line
    if len(sys.argv) > 1:
        test_url = sys.argv[1]

    print("=" * 80)
    print("Article Extractor - Multi-Article Content Detection")
    print("=" * 80)
    print(f"\nExtracting from: {test_url}\n")

    extractor = ArticleExtractor()

    try:
        result = extractor.extract_all(test_url, print_cleaned_html=True)

        print("\n" + "=" * 80)
        print(f"EXTRACTION RESULTS: {len(result.articles)} article(s) found")
        print("=" * 80)

        for i, article in enumerate(result.articles):
            print(f"\n{'=' * 40}")
            print(
                f"ARTICLE {i + 1} {'(PRIMARY)' if article.is_primary else '(RELATED)'}")
            print("=" * 40)
            print(f"Title: {article.title}")
            print(f"Author: {article.author}")
            print(f"Date: {article.publish_date}")
            print(f"Main Image: {article.main_image}")
            print(f"Paragraphs found: {len(article.paragraphs)}")
            print(f"\n{'-' * 40}")
            print("CONTENT:")
            print("-" * 40)

            if article.content:
                word_count = len(article.content.split())
                # Truncate for display
                display_content = article.content[:2000]
                if len(article.content) > 2000:
                    display_content += "\n... [truncated]"
                print(f"\n{display_content}")
                print(
                    f"\n[Total: {word_count} words, {len(article.paragraphs)} paragraphs]")
            else:
                print("\nNo content could be extracted.")

        # Show related article links (lazy-loaded)
        if result.related_article_links:
            print(f"\n{'=' * 40}")
            print(
                f"RELATED ARTICLE LINKS ({len(result.related_article_links)} found)")
            print("=" * 40)
            for link in result.related_article_links[:10]:
                print(f"\n  - {link['title']}")
                print(f"    {link['url']}")

    except requests.RequestException as e:
        print(f"\nError fetching URL: {e}")
    except Exception as e:
        print(f"\nError extracting content: {e}")
        import traceback
        traceback.print_exc()
