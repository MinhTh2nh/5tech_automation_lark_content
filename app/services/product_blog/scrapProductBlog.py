from app.helpers.five_tech.scrapper import scrape_content_blog, scrape_images, scrape_tech_specs
from app.services.browser import initialize_browser_without_stealth
from app.services.product_blog.routes import handle_route

async def scrap_product_blog(list_of_items):
        browser, page, playwright = await initialize_browser_without_stealth(headless=False)
        results = []

        for item in list_of_items:
            await page.route("**/*", handle_route)
            
            link_content_crawl = item.get("post_content")
            link_images_crawl = item.get("Hình ảnh")
            link_techspecs_crawl = item.get("Thông số kỹ thuật")
            post_title = item.get("post_title", "")

            result = {
                "post_title": item.get("post_title"),
                "craw_content_blog": [],
                "list_of_featured_images": [],
                "craw_data_technical_specification": [],
                "meta:_yoast_wpseo_focuskw": item.get("meta:_yoast_wpseo_focuskw"),
                "meta:_yoast_wpseo_metadesc": item.get("meta:_yoast_wpseo_metadesc"),
                "meta:_yoast_wpseo_title": item.get("meta:_yoast_wpseo_title"),
                "sku": item.get("sku")
            }

            if link_content_crawl:
                result["craw_content_blog"] = await scrape_content_blog(
                    page = page, 
                    url=link_content_crawl
                )
            else:
                result["craw_content_blog"] = []
            
            if link_images_crawl:
                result["list_of_featured_images"] = await scrape_images(
                    page= page, 
                    url=link_images_crawl
                )
            else:
                result["list_of_featured_images"] = []

            if link_techspecs_crawl:
                result["craw_data_technical_specification"] = await scrape_tech_specs(
                    page=page, 
                    url=link_techspecs_crawl
                )
            else:
                result["craw_data_technical_specification"] = []

            print("Finished scraping for:", post_title)
            results.append(result)

        await browser.close()
        await playwright.stop()
        return results
