from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def scrap_content_blog(
    list_craw_websites,
    content_selector="body div",
    unwanted_selectors=None
):
    if unwanted_selectors is None:
        unwanted_selectors = ['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
            timeout=60000
        )
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            viewport={"width": 1920, "height": 1080},
        )
        page = await browser_context.new_page()
        stealth_async(page)

        for website in list_craw_websites:
            url = website.get("content_blog_url")
            if not url:
                continue 
            try:
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
