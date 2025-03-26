from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException
from app.services.scrapContentBlog import scrap_content_blog
from app.utils.logging_config import logger
from app.services.technical_specification import (
    ruijienetworks, vn_ruijienetworks, store_ui, 
    buy_hpe_dotcom, aruba_vn, aruba_instanton, 
    tech_specs_ui, mikrotik, hpe_psnow
)
router = APIRouter()

@router.post("/craw")
async def technical_specification_crawler(request: Request):
    try:
        data = await request.json()
        url = data.get("domain_url")
        list_craw_websites = data.get("list_craw_websites")

        if not url:
            raise HTTPException(status_code=400, detail="Missing 'domain_url' in request.")

        # Mapping URL patterns to respective scraper functions
        scrapers = {
            "vn.ruijienetworks.com": vn_ruijienetworks.scrape_product_vn_ruijie_network,
            "ruijienetworks.com": ruijienetworks.scrape_product_ruijie_network,
            "eu.store.ui.com": store_ui.scrape_product_store_ui,
            "store.ui.com": store_ui.scrape_product_store_ui,
            "arubainstanton.com": aruba_instanton.scrape_product_aruba_instant_on,
            "aruba.com.vn": aruba_vn.scrape_product_aruba_vn,
            "buy.hpe.com": buy_hpe_dotcom.scrape_product_hpe_dot_com,
            "techspecs.ui": tech_specs_ui.scrape_product_tech_specs_ui,
            "mikrotik.com": mikrotik.scrape_product_mikrotik,
            "www.hpe.com": hpe_psnow.scrape_product_hpe_psnow_doc,
        }

        # Find matching scraper function
        for domain, scraper_function in scrapers.items():
            if domain in url:
                list_craw_websites = await scraper_function(list_craw_websites)
                return JSONResponse(
                    content={"domain_url": url, "list_craw_websites": list_craw_websites},
                    status_code=200
                )

        raise HTTPException(status_code=400, detail="Unsupported domain for crawling.")
    
    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}")
        return JSONResponse(
            content={"error": "An error occurred while processing the request.", "details": str(e)},
            status_code=500
        )

@router.post("/content_craw")
async def content_blog_crawler(request: Request):
    try:
        print("Content Blog Crawler")
        data = await request.json()
        url = data.get("domain_url")
        list_craw_websites = data.get("list_craw_websites")

        if not url:
            raise HTTPException(status_code=400, detail="Missing 'domain_url' in request.")
        
        domain_handler = None
        print("URL: ", url)
        try:
            if 'performancenetworks' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.main-content .row .post-content .row_col_wrap_12',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']
                )
            elif 'https://myplace.app' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.fl-row .fl-row-content-wrap .fl-row-content .fl-col-group .fl-col-small-custom-width .fl-node-content .fl-module .fl-node-content .fl-rich-text',
                )
            elif 'https://avsystem.com' in url:
                print("AV System")
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.body-wrapper .body-container-wrapper .body-container .container .blog-wrapper .post-wrapper',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.blog-post__contact-banner', '.blog-post__share']
                )
            elif 'https://pocketstop.com' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.post-template-default .site-container',
                    unwanted_selectors=['script', 'form', 'header', 'footer', 'style', '.blog-post__share', '.blog-post__contact-banner', '.contact-section', '.rp4wp-related-posts', '.date-category', '.sidebar']
                )
            elif 'https://connect.quik.vn' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.e-con-inner .max-width-blog .e-child',
                )
            elif 'https://www.searchenginejournal.com' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.post-template-default #main-content .container-lg .row .s-post-section article.post',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                        '.module', '.channel', '.bottom-cat narrow-cont', '.sej-article-head byline', '.sej-under-post sej-under-post_1']
                )
            elif 'https://martech.org' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.template-article .page-container .main-container-wrap .container-fluid .content .row .article-content',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button',
                                        '.module', '.channel', '.dateline', '#st-1', '.google-news-link',
                                        '.body-content .row', 'em']
                )
            elif 'digitalagencynetwork' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.post-template-default #wrapper .thb-page-main-content-container .thb-page-content-container-left .main-post',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.thb-post-bottom-single']
                )
            elif 'https://www.mywifinetworks.com' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='.post-template-default #page .site-content .elementor-section-wrap .elementor-section .elementor-widget-wrap',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button', '.module', '.elementor-col-33']
                )
            elif 'https://mailchimp.com' in url:
                domain_handler = await scrap_content_blog(
                    list_craw_websites,
                    content_selector='#content .layout .content .content--main',
                    unwanted_selectors=['script', 'iframe', 'style', 'noscript', 'form', 'footer', 'header', 'button']
                )
            else:
                domain_handler = await scrap_content_blog(list_craw_websites)

            list_craw_websites = domain_handler

            return JSONResponse(
                content={"content_blog_url": url, "list_craw_websites": list_craw_websites},
                status_code=200
            )

        except Exception as crawl_error:
            logger.error(f"Error during crawling for URL {url}: {str(crawl_error)}", exc_info=True)
            logger.info(f"URL: {url}")
            logger.info(f"URL---------: {url}")
            logger.error(crawl_error)
            return JSONResponse(
                content={"error": "Crawling failed.", "details": str(crawl_error)},
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error in content_blog_crawler: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": "An error occurred while processing the request.", "details": str(e)},
            status_code=500
        )


@router.post("/image_craw")
async def product_images_crawler(request: Request):
    try:
        data = await request.json()
        return JSONResponse(
            content={
                "status": "success",
                "message": "Data processed successfully"
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/image_craw_for_wp_media")
async def wp_images_crawler(request: Request):
    try:
        data = await request.json()
        return JSONResponse(
            content={
                "status": "success",
                "message": "Data processed successfully"
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")