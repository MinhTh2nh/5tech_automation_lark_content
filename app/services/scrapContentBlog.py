from playwright.async_api import async_playwright

async def scrap_content_blog(
    list_craw_websites,
    content_selector="body div",
    unwanted_selectors=None
):
    """
    Asynchronously scrapes content from a list of websites using Playwright.

    :param list_craw_websites: List of dictionaries containing URLs to scrape.
    :param content_selector: CSS selector to extract the main content.
    :param unwanted_selectors: List of CSS selectors for elements to remove.
    :return: List of dictionaries containing scraped content.
    """
    if unwanted_selectors is None:
        unwanted_selectors = ['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        print("Scraping content...")

        for website in list_craw_websites:
            url = website.get("content_blog_url")
            if not url:
                continue  # Skip if no URL is provided

            try:
                # Route interception to block unwanted requests
                async def handle_route(route):
                    blocked_patterns = ['ads', 'doubleclick.net', 'googlesyndication.com']
                    if any(pattern in route.request.url for pattern in blocked_patterns):
                        await route.abort()
                    else:
                        await route.continue_()

                await page.route("**/*", handle_route)

                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_load_state(state="networkidle")
                await page.wait_for_selector(selector=content_selector)

                extracted_content = await page.evaluate('''(args) => {
                    const [contentSelector, unwantedSelectors] = args;
                    const elements = document.querySelectorAll(contentSelector);
                    
                    elements.forEach(el => {
                        unwantedSelectors.forEach(selector => {
                            el.querySelectorAll(selector).forEach(node => node.remove());
                        });
                    });

                    const extractText = (element) => {
                        let result = '';
                        element.childNodes.forEach(node => {
                            if (node.nodeType === Node.TEXT_NODE) {
                                result += node.textContent.trim() + ' ';
                            } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'IMG') {
                                result += node.outerHTML;  // Keep <img> tags
                            } else if (node.nodeType === Node.ELEMENT_NODE) {
                                result += extractText(node);
                            }
                        });
                        return result.trim();
                    };

                    let content = '';
                    elements.forEach(el => {
                        content += extractText(el) + '\\n\\n';
                    });
                    return content.trim();
                }''', [content_selector, unwanted_selectors])

                website["craw_content_blog"] = [{"translatedText": extracted_content}]

            except Exception as scraping_err:
                print(f"Scraping error for URL {url}: {scraping_err}")
                website["craw_content_blog"] = []

        await browser.close()
        return list_craw_websites
