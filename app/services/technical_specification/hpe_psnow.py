from playwright.async_api import async_playwright
import asyncio

async def scrape_product_hpe_psnow_doc(list_craw_websites):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()
        await page.set_user_agent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        try:
            for website in list_craw_websites:
                url = website.get('technical_specification_url')
                try:
                    await page.goto(url, wait_until='networkidle')
                    
                    craw_data = await page.evaluate('''() => {
                        let productList = [];
                        let tbodyElements = document.querySelectorAll('#mainContainer .titleSpace #Technical_Specifications_4_content .section .QSBorders tbody');
                        tbodyElements.forEach(tbody => {
                            let rows = tbody.querySelectorAll('tr');
                            if (rows.length > 0) {
                                let modelName = rows[0]?.innerText.trim();
                                let technicalData = {};
                                rows.forEach(row => {
                                    let tds = row.querySelectorAll('td');
                                    if (tds.length === 2) {
                                        let key = tds[0]?.innerText.trim();
                                        let value = tds[1]?.innerText.trim();
                                        if (value.includes('\\n')) {
                                            let nestedDetails = value.split('\\n')
                                                .map(line => line.trim())
                                                .filter(line => line !== "");
                                            technicalData[key] = nestedDetails;
                                        } else {
                                            technicalData[key] = value;
                                        }
                                    } else if (tds.length === 3) {
                                        let key = tds[1]?.innerText.trim();
                                        let value = tds[2]?.innerText.trim();
                                        if (value.includes('\\n')) {
                                            let nestedDetails = value.split('\\n')
                                                .map(line => line.trim())
                                                .filter(line => line !== "");
                                            technicalData[key] = nestedDetails;
                                        } else {
                                            technicalData[key] = value;
                                        }
                                    }
                                });
                                if (modelName && Object.keys(technicalData).length > 0) {
                                    productList.push({
                                        model_name: modelName,
                                        technical_information: technicalData
                                    });
                                }
                            }
                        });
                        console.log(productList);
                        return productList;
                    }''')
                    
                    print(craw_data)
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