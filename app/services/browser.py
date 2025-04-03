from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def initialize_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=headless,
        timeout=20000,
    )
    browser_context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    )
    page = await browser_context.new_page()
    await stealth_async(page)
    return browser, page, playwright

async def initialize_browser_without_stealth(headless=True):
    playwright = await async_playwright().start() 
    browser = await playwright.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
        timeout=20000,
    )
    browser_context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    )
    page = await browser_context.new_page()
    return browser, page, playwright
