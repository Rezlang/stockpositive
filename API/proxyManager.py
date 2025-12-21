from playwright.async_api import async_playwright
import random

PROXIES = [
    "http://user:pass@ip1:port",
    "http://user:pass@ip2:port",
    "http://user:pass@ip3:port",
]


class BrowserSession:
    def __init__(
        self,
        user_data_dir=None,
        headless=True,
        args=None,
        proxy=None
    ):
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.args = args or []
        self.proxy = proxy or self._pick_proxy()

        self.playwright = None
        self.browser_context = None

    def _pick_proxy(self):
        return random.choice(PROXIES)

    async def start(self):
        self.playwright = await async_playwright().start()

        launch_options = {
            "headless": self.headless,
            "args": self.args,
            "proxy": {"server": self.proxy},
        }

        if self.user_data_dir:
            self.browser_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                **launch_options
            )
        else:
            browser = await self.playwright.chromium.launch(**launch_options)
            self.browser_context = await browser.new_context()

    async def new_page(self):
        if not self.browser_context:
            raise RuntimeError("Session not started")

        return await self.browser_context.new_page()

    async def close(self):
        if self.browser_context:
            await self.browser_context.close()
        if self.playwright:
            await self.playwright.stop()
