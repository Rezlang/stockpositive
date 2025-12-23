from playwright.sync_api import sync_playwright
import os

URL = "https://old.reddit.com/r/wallstreetbets/"


def init_browser(p):
    context = p.chromium.launch_persistent_context(
        user_data_dir="./reddit_profile",
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )

    page = context.new_page()

    page.set_extra_http_headers({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    })

    page.goto(URL, timeout=90000)
    print("Browser initialized. If needed, log in manually. Cookies saved.")

    return context, page


def scrape_wsb_posts(context):
    page = context.new_page()

    page.set_extra_http_headers({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    })

    page.goto(URL, timeout=60000)
    page.wait_for_selector("div.thing", timeout=30000)

    posts = page.locator("div.thing")
    count = posts.count()

    scraped = []
    discarded = []

    for i in range(min(25, count)):
        post = posts.nth(i)

        flair_el = post.locator("span.linkflairlabel")
        flair = flair_el.inner_text().strip() if flair_el.count() > 0 else ""

        title = post.locator("a.title").inner_text()
        link = post.locator("a.title").get_attribute("href")

        if flair.lower() == "meme":
            discarded.append({"title": title, "link": link, "reason": "meme"})
            continue

        scraped.append({"title": title, "link": link})

    return scraped, discarded


def filter_internal_links(scraped):
    valid = []
    discarded = []

    for item in scraped:
        link = item["link"] or ""
        if link.startswith("/r/"):
            valid.append(item)
        else:
            discarded.append(
                {"title": item["title"], "link": link, "reason": "external"}
            )
    return valid, discarded


def scrape_post_details(context, post_link):
    page = context.new_page()

    full_url = "https://old.reddit.com" + post_link

    page.set_extra_http_headers({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    })

    page.goto(full_url, timeout=60000)
    page.wait_for_selector("div.top-matter", timeout=30000)

    title = page.locator("a.title").inner_text()

    body_el = page.locator("div.expando div.md")
    body = body_el.inner_text().strip() if body_el.count() > 0 else ""

    # Get post upvotes ("score")
    post_score_el = page.locator("div.score.unvoted")
    post_score = post_score_el.inner_text().strip() if post_score_el.count() > 0 else ""

    # Scrape all comments + comment upvotes in one JS call
    comments = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll("div.comment")).map(c => {
                const author = c.querySelector("p.tagline > .author")?.innerText || "";
                const text = c.querySelector("div.md")?.innerText.trim() || "";
                const score = c.querySelector(".score.unvoted")?.innerText.trim() || "";
                return { author, text, score };
            }).filter(c => c.text);
        }
    """)

    return title, body, post_score, comments


def main():
    profile_dir = "./reddit_profile"

    def profile_exists_and_not_empty(path):
        return os.path.exists(path) and os.listdir(path)

    with sync_playwright() as p:
        if not profile_exists_and_not_empty(profile_dir):
            print("Initializing browser (first run, no profile found)...")
            context, _ = init_browser(p)
            context.close()
            print("Initialization complete. Restart script to scrape.")
            return
        else:
            print("profile exists")
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )

        scraped, discarded_memes = scrape_wsb_posts(context)

        print("Discarded meme posts:")
        for d in discarded_memes:
            print(d)

        valid, discarded_external = filter_internal_links(scraped)

        print("\nDiscarded external links:")
        for d in discarded_external:
            print(d)

        print("\nValid scraped posts:")
        for v in valid:
            print({"title": v["title"], "link": v["link"]})

        if not valid:
            print("No valid /r/ links to scrape further.")
            context.close()
            return

        post_to_scrape = valid[0]["link"]

        title, body, post_score, comments = scrape_post_details(
            context, post_to_scrape)

        print("\nSelected Post Details:")
        print("Title:", title)
        print("Score:", post_score)
        print("Body:", body)
        print("Total Comments:", len(comments))

        print("\nComments:")
        for c in comments:
            print(c)

        context.close()


if __name__ == "__main__":
    main()
