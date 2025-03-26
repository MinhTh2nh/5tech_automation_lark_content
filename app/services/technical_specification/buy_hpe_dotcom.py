from playwright.async_api import async_playwright
import asyncio

async def scrape_product_hpe_dot_com(url):
    print(f"scrape product from {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        
        await page.goto(url, wait_until='networkidle')  # Note: 'networkidle0' becomes 'networkidle' in Python
        
        products = await scrape_product_wlan_access_point(page)
        
        await browser.close()
        return products

async def scrape_product_wlan_access_point(page):
    async def result_fetching():
        return await page.evaluate('''async () => {
            return await new Promise(resolve => {
                let products = [];
                try {
                    let productWrapper = document.querySelectorAll('.hpeit-pdp-container #specification .hpeit-modal .padd #displayProductSpecification .hpe-more-information__list-item_tabs_sepcifications');
                    productWrapper.forEach((row) => {
                        let dataJson = {};
                        try {
                            let key = row.querySelector('span b')?.innerText.trim() || '';
                            let value = row.querySelector('span.hpe-product-specification-text')?.innerText.trim() || '';
                            console.log("value", value);
                            console.log("key", key);
                            if (key && value) {
                                dataJson[key] = value;
                            }
                        } catch (err) {
                            console.error('Error processing row:', err);
                        }
                        if (Object.keys(dataJson).length > 0) {
                            products.push(dataJson);
                        }
                    });
                    console.log('Products:', products);
                } catch (err) {
                    console.error("Error in evaluate:", err);
                }
                resolve(products);
            });
        }''')
    
    return await result_fetching()