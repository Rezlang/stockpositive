from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import time

from typing import List
from companies import COMPANIES


def contains_company_mention(text: str) -> bool:
    """Check if text contains any company name or ticker"""
    text_upper = text.upper()

    for company in COMPANIES:
        # Check company names
        for name in company.names:
            if name.upper() in text_upper:
                return True

        # Check tickers
        for ticker in company.tickers:
            if ticker.upper() in text_upper:
                return True

    return False


def scrape_article_content(page, url):
    """Scrape the content from a specific article page"""
    print(f"\nScraping article URL: {url}")
    print("=" * 80)

    try:
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(2)

        # Save HTML content to file for inspection
        html_content = page.content()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f'article_html_{timestamp}.html'

        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ HTML content saved to '{html_filename}'")

        article_data = {
            'url': url,
            'title': None,
            'author': None,
            'publish_date': None,
            'content': None,
            'paragraphs': []
        }

        # Try to get article title
        title_selectors = [
            'h1[data-test-locator="headline"]',
            'h1.caas-title',
            'h1',
            'article h1'
        ]

        for selector in title_selectors:
            title_elem = page.query_selector(selector)
            if title_elem:
                article_data['title'] = title_elem.inner_text().strip()
                print(f"✓ Found title: {article_data['title'][:60]}...")
                break

        # Try to get author
        author_selectors = [
            '[data-test-locator="author-name"]',
            '.caas-author-byline-collapse',
            'span[itemprop="author"]',
            '.author-name'
        ]

        for selector in author_selectors:
            author_elem = page.query_selector(selector)
            if author_elem:
                article_data['author'] = author_elem.inner_text().strip()
                print(f"✓ Found author: {article_data['author']}")
                break

        # Try to get publish date
        date_selectors = [
            'time[datetime]',
            '[data-test-locator="date"]',
            '.caas-attr-time-style'
        ]

        for selector in date_selectors:
            date_elem = page.query_selector(selector)
            if date_elem:
                article_data['publish_date'] = date_elem.get_attribute(
                    'datetime') or date_elem.inner_text().strip()
                print(f"✓ Found date: {article_data['publish_date']}")
                break

        # Try to get article content
        content_selectors = [
            '.caas-body',
            'article .body',
            '[data-test-locator="article-body"]',
            'article'
        ]

        content_found = False
        for selector in content_selectors:
            content_elem = page.query_selector(selector)
            if content_elem:
                # Get all paragraphs
                paragraphs = content_elem.query_selector_all('p')

                if paragraphs:
                    for p in paragraphs:
                        text = p.inner_text().strip()
                        if len(text) > 20:  # Filter out very short paragraphs
                            article_data['paragraphs'].append(text)

                    if article_data['paragraphs']:
                        article_data['content'] = '\n\n'.join(
                            article_data['paragraphs'])
                        print(
                            f"✓ Found {len(article_data['paragraphs'])} paragraphs")
                        content_found = True
                        break

        if not content_found:
            print("⚠ Could not extract article content")

        return article_data

    except Exception as e:
        print(f"❌ Error scraping article content: {e}")
        return None


def scrape_yahoo_finance_article():
    """Scrape the most recent article from Yahoo Finance stock market news that mentions a tracked company"""

    with sync_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the page
        url = "https://finance.yahoo.com/topic/stock-market-news/"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")

        # Wait a bit for dynamic content to load
        print("Waiting for page to fully load...")
        time.sleep(3)

        # Scroll down a bit to trigger lazy loading
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)

        # Extract the first article that mentions a tracked company
        print("Extracting first article with company mention...")

        # Strategy 1: Look for article links with specific patterns
        all_links = page.query_selector_all(
            'a[href*="/news/"], a[href*="/video/"]')

        print(f"Found {len(all_links)} potential article links...")

        article = None

        for link in all_links:
            try:
                href = link.get_attribute('href')

                if not href:
                    continue

                # Build full URL if needed
                if href.startswith('/'):
                    full_url = f"https://finance.yahoo.com{href}"
                else:
                    full_url = href

                # Skip if it's not a news article
                if '/news/' not in full_url and '/video/' not in full_url:
                    continue

                # Try to get title from various elements
                title = None

                # Try h3 first
                h3 = link.query_selector('h3')
                if h3:
                    title = h3.inner_text().strip()

                # Try h2 if h3 doesn't exist
                if not title:
                    h2 = link.query_selector('h2')
                    if h2:
                        title = h2.inner_text().strip()

                # Try getting text from link itself
                if not title:
                    title = link.inner_text().strip()

                # Clean up title
                if title:
                    title = ' '.join(title.split())  # Remove extra whitespace

                # Check if title contains a company mention
                if title and len(title) > 10:
                    if contains_company_mention(title):
                        article = {
                            'title': title,
                            'url': full_url
                        }
                        print(
                            f"  ✓ Found article with company mention: {title[:60]}...")
                        break
                    else:
                        print(
                            f"  ✗ Skipping (no company mention): {title[:60]}...")

            except Exception as e:
                continue

        # Scrape content from the article
        article_content = None
        if article:
            print("\n" + "=" * 80)
            print("Scraping content from article...")
            print("=" * 80)
            article_content = scrape_article_content(page, article['url'])

        # Close browser
        print("\nClosing browser...")
        browser.close()

        return article_content


def main():
    print("=" * 80)
    print("Yahoo Finance Stock Market News Scraper")
    print("=" * 80)
    print(f"Tracking {len(COMPANIES)} companies")
    print("=" * 80)
    print()

    try:
        # Scrape article
        article_content = scrape_yahoo_finance_article()

        if not article_content:
            print(
                "\n❌ No article found with company mentions. The page structure may have changed.")
            return

        # Display article content
        print(f"\n{'=' * 80}")
        print("ARTICLE CONTENT")
        print("=" * 80)
        print(f"\nTitle: {article_content.get('title', 'N/A')}")
        print(f"Author: {article_content.get('author', 'N/A')}")
        print(f"Date: {article_content.get('publish_date', 'N/A')}")
        print(f"URL: {article_content.get('url', 'N/A')}")
        print(f"\nContent Preview:")
        print("-" * 80)
        if article_content.get('content'):
            preview = article_content['content'][:500]
            print(
                preview + "..." if len(article_content['content']) > 500 else preview)
        else:
            print("No content available")

        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f'yahoo_finance_article_{timestamp}.json'

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'scraped_at': datetime.now().isoformat(),
                'source_url': 'https://finance.yahoo.com/topic/stock-market-news/',
                'article': article_content
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to '{json_filename}'")

        # Also save to text file with full article content
        txt_filename = f'yahoo_finance_article_{timestamp}.txt'
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("Yahoo Finance Stock Market News Article\n")
            f.write(
                f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Title: {article_content.get('title', 'N/A')}\n")
            f.write(f"Author: {article_content.get('author', 'N/A')}\n")
            f.write(f"Date: {article_content.get('publish_date', 'N/A')}\n")
            f.write(f"URL: {article_content.get('url', 'N/A')}\n\n")
            f.write("-" * 80 + "\n\n")

            if article_content.get('content'):
                f.write(article_content['content'])
            else:
                f.write("No content available")

        print(f"✓ Results also saved to '{txt_filename}'")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
