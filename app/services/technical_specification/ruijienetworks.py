from playwright.async_api import async_playwright
import asyncio

async def scrape_product_ruijie_network(list_craw_websites):
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
                        let productData = {};
                        let product_wrapper = document.querySelectorAll('.new-com-details-page .com-product-item .parameter .databox');
                        product_wrapper.forEach((row) => {
                            try {
                                let key = row.querySelector('.th')?.innerText.trim() || '';
                                let value = row.querySelector('.td')?.innerText.trim() || '';
                                
                                if (key && value) {
                                    productData[key] = value;
                                }
                            } catch (err) {
                                console.error('Error processing row:', err);
                            }
                        });
                        console.log(productData);
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