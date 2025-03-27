from app.services.images_dowload import wp_images_crawler_controller
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException
from app.services.product_blog.scrapProductBlog import scrap_product_blog
from app.utils.logging_config import logger

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Test Route"}

@router.post("/product_post_crawl")
async def product_images_crawler_5tech(request: Request):
    try:
        data = await request.json()
        post_title = data.get("post_title")
        link_content_crawl = data.get("link_content_crawl") 
        link_images_crawl = data.get("link_images_crawl")
        link_techspecs_crawl = data.get("link_techspecs_crawl")
        domain_handler = None
        try:
            domain_handler = await scrap_product_blog(
                    post_title=post_title,
                    link_content_crawl=link_content_crawl,
                    link_images_crawl=link_images_crawl,
                    link_techspecs_crawl=link_techspecs_crawl
            )
            list_craw_websites = domain_handler
            return JSONResponse(
                content={
                    "list_craw_websites": list_craw_websites,
                    "post_title": post_title,
                    "link_content_crawl": link_content_crawl,
                    "link_images_crawl": link_images_crawl,
                    "link_techspecs_crawl": link_techspecs_crawl
                },
                status_code=200
            )
        except Exception as e:
            logger.error(f"Error scraping content: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.post("/image_craw_for_wp_media")
async def wp_images_crawler(request: Request):
    try:
        data = await request.json()
        original_list_url = data.get('original_list_url')
        image_alt_text = data.get('image_alt_text')
        new_translate_post = data.get('new_translate_post')
        try:
            result = wp_images_crawler_controller(
                original_list_url=original_list_url, 
                image_alt_text=image_alt_text, 
                new_translate_post=new_translate_post, 
                is_5tech=True)
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