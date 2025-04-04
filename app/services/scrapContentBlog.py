from app.services.browser import initialize_browser
from app.services.extractors import extract_page_content, extract_page_content_selector
from app.services.product_blog.routes import handle_route

async def scrap_content_blog(
    list_craw_websites,
    content_selector="body div",
    unwanted_selectors=None
):
    if unwanted_selectors is None:
        unwanted_selectors = ['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']

    browser, page, playwright = await initialize_browser(headless=True)
    
    for website in list_craw_websites:
        url = website.get("content_blog_url")
        if not url:
            continue 
        try:
            await page.route("**/*", handle_route)
            await page.goto(url, wait_until="load", timeout=20000)
            await page.wait_for_load_state(state="networkidle")
            await page.wait_for_selector(selector=content_selector)

            extracted_content = await extract_page_content(page, content_selector, unwanted_selectors)  # Ensure this is defined
            print("Finished scraping content", url)
            website["craw_content_blog"] = [{"translatedText": extracted_content}]

        except Exception as scraping_err:
            print(f"Scraping error for URL {url}: {scraping_err}")
            website["craw_content_blog"] = []
    await browser.close()
    await playwright.stop()
    return list_craw_websites

async def scrap_content_blog_selector(
    list_craw_websites,
    content_selector="body div",
    unwanted_selectors=None
):
    if unwanted_selectors is None:
        unwanted_selectors = ['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']

    browser, page, playwright = await initialize_browser(headless=False)
    
    for website in list_craw_websites:
        url = website.get("content_blog_url")
        if not url:
            continue 
        try:
            await page.route("**/*", handle_route)
            await page.goto(url, wait_until="load", timeout=20000)
            await page.wait_for_load_state(state="networkidle")
            await page.wait_for_selector(selector=content_selector)

            extracted_content = await extract_page_content_selector(page, content_selector, unwanted_selectors)  # Ensure this is defined
            print("Finished scraping content", url)
            website["craw_content_blog"] = [{"translatedText": extracted_content}]

        except Exception as scraping_err:
            print(f"Scraping error for URL {url}: {scraping_err}")
            website["craw_content_blog"] = []
    await browser.close()
    await playwright.stop()
    return list_craw_websites