from playwright.async_api import async_playwright
import asyncio

async def scrape_product_aruba_instant_on(list_craw_websites):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        
        try:
            for website in list_craw_websites:
                url = website.get('technical_specification_url')
                try:
                    await page.goto(url, wait_until='networkidle')
                    await page.wait_for_selector('.product-specs .container',
                        visible=True,
                        timeout=5000
                    )
                    
                    craw_data = await page.evaluate('''() => {
                        let productData = {};
                        let firstTable = document.querySelectorAll('.product-specs .container .row .block table tr');
                        if (firstTable) {
                            firstTable.forEach(row => {
                                let th = row.querySelector('th');
                                let td = row.querySelector('td');
                                if (th && td) {
                                    let key = th.innerText.trim();
                                    let value = td.innerText.trim();
                                    if (key && value) {
                                        productData[key] = value;
                                    }
                                }
                            });
                        }
                        return productData;
                    }''')
                    
                    website['craw_data_technical_specification'] = craw_data
                    
                except Exception as err:
                    print(f"Error scraping URL {url}: {err}")
                    website['craw_data_technical_specification'] = []
            
            return list_craw_websites
            
        except Exception as err:
            print(f"Error during scraping process: {err}")
            raise err
            
        finally:
            await browser.close()