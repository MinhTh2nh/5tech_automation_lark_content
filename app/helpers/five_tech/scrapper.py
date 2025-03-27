async def scrape_content_blog(page, url, content_selector, unwanted_selectors):
    print("content_selector", content_selector)
    print("unwanted_selectors", unwanted_selectors)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state(state="networkidle")

        content = await page.evaluate('''(args) => {
            const [contentSelector, unwantedSelectors] = args;
            const elements = document.querySelectorAll(contentSelector);
            
            elements.forEach(el => {
                unwantedSelectors.forEach(selector => {
                    el.querySelectorAll(selector).forEach(node => node.remove());
                });
            });

            const extractText = (element) => {
                let result = '';
                element.childNodes.forEach(node => {        
                    if (node.nodeType === Node.TEXT_NODE) {
                        result += node.textContent.trim() + ' ';
                    } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'IMG') {
                        result += node.outerHTML;
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        result += extractText(node);
                    }
                });
                return result.trim();
            };

            let content = '';
            elements.forEach(el => {
                content += extractText(el) + '\\n\\n';
            });
            return content.trim();
        }''', [content_selector, unwanted_selectors])
        
        return [{"translatedText": content}]
    except Exception as err:
        print(f"Content scraping error for URL {url}: {err}")
        return []

async def scrape_images(page, url, image_selector="img"):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state(state="networkidle")
        
        images = await page.evaluate('''(selector) => {
            const imageElements = document.querySelectorAll(selector);
            const featuredImages = [];
            imageElements.forEach(img => {
                featuredImages.push(img.src);
            });
            return featuredImages;
        }''', image_selector)
        return images
    except Exception as err:
        print(f"Images scraping error for URL {url}: {err}")
        return []

async def scrape_tech_specs(page, url, specs_selector):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state(state="networkidle")
        
        specs = await page.evaluate('''(selector) => {
            const rows = document.querySelectorAll(selector);
            const productList = [];

            rows.forEach(row => {
                const dataJson = {};
                try {
                    const tds = row.querySelectorAll('td');
                    const divs = row.querySelectorAll('div');

                    if (tds.length >= 2) {
                        // Handling table format
                        const key = tds[0]?.innerText.trim();
                        const value = tds[1]?.innerText.trim();
                        if (key && value) {
                            dataJson[key] = value;
                        }
                    } else if (divs.length >= 2) {
                        // Handling div-based key-value pairs
                        const key = divs[0]?.innerText.trim();
                        const value = divs[1]?.innerText.trim();
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
            return productList;
        }''', specs_selector)
        return specs
    except Exception as err:
        print(f"Tech specs scraping error for URL {url}: {err}")
        return []