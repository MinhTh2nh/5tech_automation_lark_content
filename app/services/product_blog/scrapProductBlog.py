from playwright.async_api import async_playwright
from app.helpers.five_tech.scrapper import scrape_content_blog, scrape_images, scrape_tech_specs

async def scrap_product_blog(list_of_items):
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
            timeout=60000 
        )
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            java_script_enabled=True,
            locale="en-US",
            timezone_id="UTC",
            geolocation=None,
            permissions=None,
            extra_http_headers=None,
            offline=False,
            http_credentials=None,
            is_mobile=False,
        )

        results = []

        for item in list_of_items:
            post_title = item.get("post_title")
            link_content_crawl = item.get("post_content")
            link_images_crawl = item.get("Hình ảnh")
            link_techspecs_crawl = item.get("Thông số kỹ thuật")
            meta_yoast_wpseo_focuskw = item.get("meta:_yoast_wpseo_focuskw")
            meta_yoast_wpseo_metadesc = item.get("meta:_yoast_wpseo_metadesc")
            meta_yoast_wpseo_title = item.get("meta:_yoast_wpseo_title")
            sku = item.get("sku")   

            page = await browser_context.new_page()

            result = {
                "post_title": post_title,
                "craw_content_blog": [],
                "list_of_featured_images": [],
                "craw_data_technical_specification": [],
                "meta:_yoast_wpseo_focuskw": meta_yoast_wpseo_focuskw,
                "meta:_yoast_wpseo_metadesc": meta_yoast_wpseo_metadesc,
                "meta:_yoast_wpseo_title": meta_yoast_wpseo_title,
                "sku": sku,
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
                            '.content-contact', '.pagination-carousel', '.pd-offer-group', '.contact', '#ProductRalated', '#right-float','img', '.addtocart', '.certelificates-list'
                    ]
                )
                elif 'https://wifi.fpt.net/' in link_content_crawl:
                    result["craw_content_blog"] = await scrape_content_blog(
                        page, 
                        url=link_content_crawl, 
                        content_selector=".product-template-default #page .container .row .site-main .woocommerce .single-product", 
                        unwanted_selectors=[
                            '#breadcrumbs', 'img', '.woocommerce-Tabs-panel.p.img', '.aligncenter', '.woocommerce-product-gallery', '#oss-related-product', '.price', "div[dir='auto']"
                        ]
                   )
                elif 'https://t2qwifi.com/' in link_content_crawl:
                    result["craw_content_blog"] = await scrape_content_blog(
                        page, 
                        url=link_content_crawl, 
                        content_selector=".tr_main .container .row .tr_block_content", 
                        unwanted_selectors=[
                            'script', 'form', 'header', 'footer', 'style', 'img', '.left_single_imgages', '.hidden_block', 
                            '.g_luot_mua', '.detail_bar', '.single_buy_group', '.nhanvien_hotro', '#thong_so', '#ez-toc-container', 'a', 'noscript'
                        ]
                    )
                # elif 'https://enootech.com/' in link_content_crawl:
                #     result["craw_content_blog"] = await scrape_content_blog(
                #         page, 
                #         url=link_content_crawl, 
                #         content_selector="#wrapwrap main .o_wsale_product_page", 
                #         unwanted_selectors=[
                #             'script', 'form', 'header', 'footer', 'style', 'img', 'a', 'noscript', '.oe_empty', '.o_wsale_product_images', '.tp-product-navigator',
                #             '.breadcrumb', '.o_product_page_reviews_link', 'form', '#product_attributes_simple', '#cfp_pop_up', '.tp-product-info-hook', 'hr', 'tp_extra_fields o_not_editable',
                #             '.tp_extra_fields', '.s_share', '#o_product_terms_and_share', '#wsale_user_email', 'input', '.tp-hook-product-tabs', '.tp-hook-accessory-products', '.tp-sticky-add-to-cart',
                #             '.o_product_feature_panel', '#specifications'
                #         ]
                #     )
                elif 'https://unifi.vn/' in link_content_crawl:
                    result["craw_content_blog"] = await scrape_content_blog(
                        page, 
                        url=link_content_crawl, 
                        content_selector=".inside-article .entry-content", 
                        unwanted_selectors=[
                            'script', 'form', 'header', 'footer', 'style', 'img', 'a', 'noscript', '.woocommerce-breadcrumb', '.woocommerce-notices-wrapper',
                            '.woocommerce-product-gallery', '.price', '.cart', '#tab-title-description', '.related'
                        ]
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
                elif 'https://store.ui.com/' in link_images_crawl:
                    result["list_of_featured_images"] = await scrape_images(
                        page, 
                        url=link_images_crawl, 
                        image_selector="#product-page .jXZICQ .KdHGZ img"
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
                elif 'https://store.ui.com/' in link_techspecs_crawl:
                    result["craw_data_technical_specification"] = await scrape_tech_specs(
                        page=page, 
                        url=link_techspecs_crawl, 
                        specs_selector="#product-page .KdHGZ .JrttX .bHvGn .jjEjYH",
                        button_to_click="Technical Specification"
                )
                else:
                    result["craw_data_technical_specification"] = []
            print("Finished scraping for:", post_title)
            results.append(result)
            await page.close()

        # await browser.close()
        return results
