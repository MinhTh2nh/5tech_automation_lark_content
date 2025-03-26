from playwright.async_api import async_playwright
import asyncio

async def scrape_product_aruba_vn(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        
        await page.goto(url)
        products = await scrape_product_technical_specification(page)
        
        await browser.close()
        return products

async def scrape_product_technical_specification(page):
    return await page.evaluate('''() => {
        let productData = {};
        let rows = document.querySelectorAll('.product-tab .tab-content #product-desc2 ul li');
        rows.forEach(row => {
            try {
                let textContent = row.innerText.trim();
                let separatorIndex = textContent.indexOf(':');
                if (separatorIndex > -1) {
                    let key = textContent.slice(0, separatorIndex).trim();
                    let value = textContent.slice(separatorIndex + 1).trim();
                    
                    if (key && value) {
                        productData[key] = value;
                    }
                }
            } catch (err) {
                console.error('Error processing row:', err);
            }
        });
        return productData;
    }''')