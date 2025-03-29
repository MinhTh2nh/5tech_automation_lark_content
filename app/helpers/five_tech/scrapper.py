async def scrape_content_blog(page, url, content_selector, unwanted_selectors):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        await page.wait_for_load_state(state="networkidle")

        content = await page.evaluate('''(args) => {
            const [contentSelector, unwantedSelectors] = args;
            const elements = document.querySelectorAll(contentSelector);
            
            elements.forEach(el => {
                unwantedSelectors.forEach(selector => {
                    el.querySelectorAll(selector).forEach(node => node.remove());
                });

                // Ensure all images are removed
                el.querySelectorAll("img").forEach(img => img.remove());
            });

            // Extract text only
            let content = '';
            elements.forEach(el => {
                content += el.innerText.trim() + '\\n';  // Use innerText instead of textContent
            });

            return content.trim();
        }''', [content_selector, unwanted_selectors])

        return [{"translatedText": content}]
    except Exception as err:
        print(f"Content scraping error for URL {url}: {err}")
        return []


async def scrape_images(page, url, image_selector="img"):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
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

async def scrape_tech_specs(page, url, specs_selector, button_to_click=None):
    try:
        await page.goto(url, wait_until="load", timeout=10000)
        await page.wait_for_load_state(state="networkidle")

        if button_to_click:
            try:
                await page.wait_for_selector("button", timeout=10000)
                buttons = await page.query_selector_all("button")

                for button in buttons:
                    text = await page.evaluate('(el) => el.textContent.trim()', button)
                    if button_to_click in text:  # Case-insensitive match
                        await button.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(5000)
                        break  
            except Exception as click_err:
                print(f"Error clicking button '{button_to_click}' at URL {url}: {click_err}")

        specs = await page.evaluate('''(selector) => {
            const rows = document.querySelectorAll(selector);
            const productList = [];

            rows.forEach(row => {
                const dataJson = {};
                try {
                    const tds = row.querySelectorAll('td, th');
                    const divs = row.querySelectorAll('div, span');

                    if (tds.length >= 2) {
                        const key = tds[0]?.innerText.trim();
                        const value = tds[1]?.innerText.trim();
                        if (key && value) dataJson[key] = value;
                    } else if (divs.length >= 2) {
                        const key = divs[0]?.innerText.trim();
                        const value = divs[1]?.innerText.trim();
                        if (key && value) dataJson[key] = value;
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
        return specs if specs else []
        
    except Exception as err:
        print(f"Tech specs scraping error for URL {url}: {err}")
        return []
