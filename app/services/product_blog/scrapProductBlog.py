from playwright.async_api import async_playwright
from app.helpers.five_tech.scrapper import scrape_content_blog, scrape_images, scrape_tech_specs
from playwright_stealth import stealth_async

async def scrap_product_blog(
    post_title,
    link_content_crawl,
    link_images_crawl,
    link_techspecs_crawl,
    content_selector='article',
    image_selector='img',
    specs_selector='table tbody tr',
    unwanted_selectors=None
):
    if unwanted_selectors is None:
        unwanted_selectors = ['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button','img']

    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
            timeout=60000  # Increase timeout (60 seconds)
        )
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
        page = await browser_context.new_page()
        stealth_async(page)

        result = {
            "craw_content_blog": [],
            "list_of_featured_images": [],
            "craw_data_technical_specification": []
        }

        async def handle_route(route):
            blocked_patterns = ['ads', 'doubleclick.net', 'googlesyndication.com']
            if any(pattern in route.request.url for pattern in blocked_patterns):
                await route.abort()
            else:
                await route.continue_()
        await page.route("**/*", handle_route)

        if link_content_crawl:
            if 'https://viettuans.vn' in link_content_crawl:
                result["craw_content_blog"] = await scrape_content_blog(
                    page, 
                    url=link_content_crawl, 
                    content_selector="body .t3-wrapper #main-body .single-product #product-view .product-content", 
                    unwanted_selectors=[
                        'script', 'form', 'header', 'footer', 'style', '.product_sidebar', '.hidden', '.more_technical', '.rating-star', '.rating-star2', '.price-big', '.product-desc',    
                        '.blog-post__share', '.blog-post__contact-banner', '.contact-section', '#ProductRating', '.contact-heading','.col-lg-3', '.list_attribute',
                        '.content-contact', '.pagination-carousel', '.pd-offer-group', '.contact', '#ProductRalated', '#right-float','img', '.addtocart', '.certificates-list'
                    ]
                )
            else:
                result["craw_content_blog"] = await scrape_content_blog(
                page, link_content_crawl, content_selector, unwanted_selectors
            )
        else:
            result["craw_content_blog"] = []

        if link_images_crawl:
            if 'https://viettuans.vn' in link_images_crawl:
                result["list_of_featured_images"] = await scrape_images(
                    page, 
                    url=link_images_crawl, 
                    image_selector=".product .t3-wrapper #main-body .single-product .product-view .product-content .product-top .product-image-wrap img"
                )
            elif 'https://techspecs.ui.com/' in link_images_crawl:
                result["list_of_featured_images"] = await scrape_images(
                    page, 
                    url=link_images_crawl, 
                    image_selector=".cdrVYk .hkSLYn .gmpZJz img"
                )
            else:
                result["list_of_featured_images"] = await scrape_images(
                page, link_images_crawl, image_selector
            )
        else:
            result["list_of_featured_images"] = []

        if link_techspecs_crawl:
            if 'https://viettuans.vn' in link_techspecs_crawl:
                result["craw_data_technical_specification"] = await scrape_tech_specs(
                    page=page, 
                    url=link_techspecs_crawl, 
                    specs_selector=".product_sidebar .hidden-sm table tbody tr"
                )
            elif 'https://techspecs.ui.com/' in link_techspecs_crawl:
                result["craw_data_technical_specification"] = await scrape_tech_specs(
                    page=page, 
                    url=link_techspecs_crawl, 
                    specs_selector=".eGOVDM .egaTkP .hthDOj"
            )
            else: 
                result["craw_data_technical_specification"] = await scrape_tech_specs(
                page, link_techspecs_crawl, specs_selector
            )
        else:
            result["craw_data_technical_specification"] = []
        await browser.close()
        return result