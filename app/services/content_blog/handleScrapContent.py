from fastapi import HTTPException, logger
from fastapi.responses import JSONResponse
from app.services.browser import initialize_browser
from app.services.content_blog.scrapContentBlog import scrap_content_blog, scrap_content_blog_selector
from app.services.product_blog.routes import handle_route

async def handle_scrap_content(list_of_items):
        browser, page, playwright = await initialize_browser(headless=True)
        results = []
        try:
            for item in list_of_items:
                await page.route("**/*", handle_route)
                
                url = item.get("domain_url")
                list_craw_websites = item.get("list_craw_websites")

                if not url:
                    raise HTTPException(status_code=400, detail="Missing 'domain_url' in request.")
            
                domain_handler = None
                try:
                    if 'performancenetworks' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            content_selector='.main-content .row .post-content .row_col_wrap_12',
                            page=page,
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']
                        )
                    elif 'https://myplace.app' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.fl-row .fl-row-content-wrap .fl-row-content .fl-col-group .fl-col-small-custom-width .fl-node-content .fl-module .fl-node-content .fl-rich-text',
                        )   
                    elif 'https://avsystem.com' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.body-wrapper .body-container-wrapper .body-container .container .blog-wrapper .post-wrapper',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.blog-post__contact-banner', '.blog-post__share']
                        )
                    elif 'https://pocketstop.com' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.post-template-default .site-container',
                            unwanted_selectors=['script', 'form', 'header', 'footer', 'style', '.blog-post__share', '.blog-post__contact-banner', '.contact-section', '.rp4wp-related-posts', '.date-category', '.sidebar']
                        )
                    elif 'https://connect.quik.vn' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.e-con-inner .max-width-blog .e-child',
                        )
                    elif 'https://www.searchenginejournal.com' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.post-template-default #main-content .container-lg .row .s-post-section article.post',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                                '.module', '.channel', '.bottom-cat narrow-cont', '.sej-article-head byline', '.sej-under-post sej-under-post_1']
                        )
                    elif 'https://martech.org' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.template-article .page-container .main-container-wrap .container-fluid .content .row .article-content',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                                '.module', '.channel', '.dateline', '#st-1', '.google-news-link',
                                                '.body-content .row', 'em']
                        )
                    elif 'digitalagencynetwork' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.post-template-default #wrapper .thb-page-main-content-container .thb-page-content-container-left .main-post',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.thb-post-bottom-single']
                        )
                    elif 'https://www.mywifinetworks.com' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.post-template-default #page .site-content .elementor-section-wrap .elementor-section .elementor-widget-wrap',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.module', '.elementor-col-33']
                        )
                    elif 'https://mailchimp.com' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='#content .layout .content .content--main',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']
                        )
                    elif 'https://beambox.com/' in url:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.articles .main',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                                '.info-line', '#sidebar-left', '#sidebar-right', '.inline-trial-cta']
                        )
                    elif 'networkcomputing' in url:
                        print("Crawling Network Computing")
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page,
                            content_selector='.brand-networkcomputing .Provider .Layout .Layout-Section .TwoColumnLayout',
                            unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                                '.ArticleBase-Topics', '.TwoColumnLayout-Sidebar', '.ArticleBase-Contributors', '.ArticleBase-ContributorsWrapper',
                                                '.Resources_article', '.IirisRecommendation-Title', '.SubscribeBannerTopicPage', 'hr', '.iiris-container']
                        )
                    elif 'https://www.cnet.com' in url:
                        domain_handler = await scrap_content_blog_selector(
                            list_craw_websites,
                            page=page,
                            content_selector="div[section='article-body'].g-grid-container .u-grid-columns",
                            unwanted_selectors=["script", "iframe", "style", "noscript", "form", "footer", "header", "button",
                                                ".c-adDisplay_container", "div[data-cy='shortcodeListicle']"]
                        )
                    else:
                        domain_handler = await scrap_content_blog(
                            list_craw_websites,
                            page=page
                        )

                    results.append({
                        "content_blog_url": url,
                        "list_craw_websites": domain_handler
                    })

                except Exception as crawl_error:
                    logger.error(f"Error during crawling for URL {url}: {str(crawl_error)}", exc_info=True)
                    results.append({
                        "error": "Crawling failed",
                        "url": url,
                        "details": str(crawl_error)
                    })
        finally:
            await browser.close()
            await playwright.stop()

        return results