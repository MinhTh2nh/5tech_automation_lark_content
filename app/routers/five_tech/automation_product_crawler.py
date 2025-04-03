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
        list_of_items = data.get("list_of_items", [])[:4]

        if not list_of_items:
            raise HTTPException(status_code=400, detail="list_of_items cannot be empty")
        results = await scrap_product_blog(list_of_items)
        return JSONResponse(content={"scraped_results": results}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    
@router.post("/image_craw_for_wp_media")
async def wp_images_crawler(request: Request):
    try:
        data = await request.json()
        list_of_items = data.get("list_of_items", [])
        if not list_of_items:
            raise HTTPException(status_code=400, detail="list_of_items cannot be empty")
        results = wp_images_crawler_controller(list_of_items, is_5tech=True)
        return JSONResponse(content={"scraped_results": results}, status_code=200)
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")