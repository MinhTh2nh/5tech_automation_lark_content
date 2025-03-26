from playwright.async_api import async_playwright
import asyncio

async def scrape_product_mikrotik(list_craw_websites):
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
                    
                    craw_data = await page.evaluate('''() => {
                        let productList = [];
                        let rows = document.querySelectorAll('.product-page .tabs-content #specifications .product-table tbody tr');
                        rows.forEach(row => {
                            let dataJson = {};
                            try {
                                let tds = row.querySelectorAll('td');
                                if (tds.length >= 2) {
                                    let key = tds[0]?.innerText.trim();
                                    let value = tds[1]?.innerText.trim();
                                    if (key && value) {
                                        dataJson[key] = value;
                                    }
                                }
                            } catch (err) {
                                console.error('Error processing row:', err);
                            }
                            if (Object.keys(dataJson).length > 0) {
                                productList.push(dataJson);
                            }
                        });
                        console.log(productList);
                        return productList;
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