from playwright.async_api import async_playwright
import asyncio

async def scrape_product_vn_ruijie_network(list_crawl_websites):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        try:
            for website in list_crawl_websites:
                url = website["technical_specification_url"]
                try:
                    await page.goto(url, wait_until='networkidle')
                    url_segments = url.split('/')
                    product_type = url_segments[4] if len(url_segments) > 4 else ""
                    
                    scraper_mapping = {
                        "wall-plate-access-points": scrape_wall_plate_access_points,
                        "indoor-access-point-series": scrape_indoor_access_points,
                        "cloud-managed-ap": scrape_wireless_cloud_managed_ap,
                        "cloud-managed-wireless": scrape_wireless_cloud_managed_ap,
                        "reyee-switch": scrape_reyee_switch,
                        "REYEE-MeshWi-Fi": scrape_reyee_mesh_wifi,
                    }
                    
                    craw_data = await scraper_mapping.get(product_type, lambda p: {})(page)
                    website["craw_data_technical_specification"] = craw_data
                    
                except Exception as e:
                    print(f"Error scraping URL {url}: {e}")
                    website["craw_data_technical_specification"] = {}
        
            return list_crawl_websites
        
        finally:
            await browser.close()

async def scrape_wall_plate_access_points(page):
    return await page.evaluate("""
        () => {
            let productData = {};
            document.querySelectorAll('.product-details-content .product-jscs table tbody tr').forEach(row => {
                let tds = row.querySelectorAll('td');
                if (tds.length >= 2) {
                    let key = tds[0]?.innerText.trim() || '';
                    let value = tds[1]?.innerText.trim() || '';
                    if (key && value) {
                        productData[key] = value;
                    }
                }
            });
            return productData;
        }
    """)

async def scrape_indoor_access_points(page):
    return await scrape_wall_plate_access_points(page)

async def scrape_reyee_mesh_wifi(page):
    return await page.evaluate("""
        () => {
            let productData = {};
            document.querySelectorAll('.new-com-details-page .parameter .databox').forEach(row => {
                let key = row.querySelector('.th')?.innerText.trim() || '';
                let value = row.querySelector('.td')?.innerText.trim() || '';
                if (key && value) {
                    productData[key] = value;
                }
            });
            return productData;
        }
    """)

async def scrape_reyee_switch(page):
    return await page.evaluate("""
        () => {
            let productData = {};
            document.querySelectorAll('.n-specification-table .n-specification-table-row').forEach(row => {
                row.querySelectorAll('.n-specification-table-data').forEach(td => {
                    let key = td.querySelector('.n-specification-table-head')?.innerText.trim() || '';
                    let value = td.querySelector('.n-specification-table-cell')?.innerText.trim() || '';
                    if (key && value) {
                        productData[key] = value;
                    }
                });
            });
            return productData;
        }
    """)

async def scrape_wireless_cloud_managed_ap(page):
    return await page.evaluate("""
        () => {
            let productData = {};
            document.querySelectorAll('.com-product-QA-main table tbody tr').forEach(row => {
                let tds = row.querySelectorAll('td');
                if (tds.length >= 2) {
                    let key = tds[0]?.innerText.trim() || '';
                    let value = tds[1]?.innerText.trim() || '';
                    if (key && value) {
                        productData[key] = value;
                    }
                }
            });
            return productData;
        }
    """)