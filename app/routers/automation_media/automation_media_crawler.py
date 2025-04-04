from app.services.content_blog.handleScrapContent import handle_scrap_content
from app.services.images_dowload import wp_images_crawler_controller, wp_images_crawler_controller_content
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException
from app.services.content_blog.scrapContentBlog import scrap_content_blog, scrap_content_blog_selector
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
        data = await request.json()
        list_of_items = data.get("list_of_items", [])
        if not list_of_items:
            raise HTTPException(status_code=400, detail="list_of_items cannot be empty")
        results = await handle_scrap_content(list_of_items)
        return JSONResponse(content={"scraped_results": results}, status_code=200)

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
        original_list_url = data.get('original_list_url')
        image_alt_text = data.get('image_alt_text', 'connect-quik')
        new_translate_post = data.get('new_translate_post')
        try:
            result = wp_images_crawler_controller_content(original_list_url, image_alt_text, new_translate_post)
            uploaded_urls = result['uploaded_urls']
            updated_translate_post = result['updated_translate_post']
        
            return JSONResponse(
                    content={
                        "original_list_url": original_list_url,
                        "response_list_url": uploaded_urls,
                        "new_translate_post": updated_translate_post
                    },
                    status_code=200
                )
        except Exception as e:
            logger.error(f"Error in wp_images_crawler: {str(e)}", exc_info=True)
            return JSONResponse(
                content={"error": "An error occurred while processing the request.", "details": str(e)},
                status_code=500
            )
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    