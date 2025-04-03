async def scrape_content_blog(page, url):
    """Scrape content based on URL by setting content_selector and unwanted_selectors internally."""
    try:
        content_selector = ""
        unwanted_selectors = []

        if 'https://viettuans.vn' in url:
            content_selector = "body .t3-wrapper #main-body .single-product #product-view .product-content"
            unwanted_selectors = [
                'script', 'form', 'header', 'footer', 'style', '.product_sidebar', '.hidden', '.more_technical', '.rating-star', 
                '.rating-star2', '.price-big', '.product-desc', '.blog-post__share', '.blog-post__contact-banner', '.contact-section', 
                '#ProductRating', '.contact-heading', '.col-lg-3', '.list_attribute', '.content-contact', '.pagination-carousel', 
                '.pd-offer-group', '.contact', '#ProductRalated', '#right-float', 'img', '.addtocart', '.certelificates-list'
            ]
        elif 'https://wifi.fpt.net/' in url:
            content_selector = ".product-template-default #page .container .row .site-main .woocommerce .single-product"
            unwanted_selectors = [
                '#breadcrumbs', 'img', '.woocommerce-Tabs-panel.p.img', '.aligncenter', '.woocommerce-product-gallery', 
                '#oss-related-product', '.price', "div[dir='auto']"
            ]
        elif 'https://t2qwifi.com/' in url:
            content_selector = ".tr_main .container .row .tr_block_content"
            unwanted_selectors = [
                'script', 'form', 'header', 'footer', 'style', 'img', '.left_single_imgages', '.hidden_block', 
                '.g_luot_mua', '.detail_bar', '.single_buy_group', '.nhanvien_hotro', '#thong_so', '#ez-toc-container', 'a', 'noscript'
            ]
        elif 'https://unifi.vn/' in url:
            content_selector = ".inside-article .entry-content"
            unwanted_selectors = [
                'script', 'form', 'header', 'footer', 'style', 'img', 'a', 'noscript', '.woocommerce-breadcrumb', 
                '.woocommerce-notices-wrapper', '.woocommerce-product-gallery', '.price', '.cart', '#tab-title-description', '.related'
            ]
        else:
            return [{"translatedText": ""}]

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


async def scrape_images(page, url):
    """Scrape images based on URL by setting image_selector internally."""
    try:
        image_selector = ""

        if 'https://viettuans.vn' in url:
            image_selector = ".product .t3-wrapper #main-body .single-product .product-view .product-content .product-top .product-image-wrap img"
        elif 'https://techspecs.ui.com/' in url:
            image_selector = ".cdrVYk .hkSLYn .gmpZJz img"
        elif 'https://store.ui.com/' in url:
            image_selector = "#product-page .jXZICQ .KdHGZ img"
        else:
            return []

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

async def scrape_tech_specs(page, url):
    """Scrape technical specifications based on URL by setting specs_selector internally."""
    try:
        specs_selector = ""
        button_to_click = None

        if 'https://viettuans.vn' in url:
            specs_selector = ".product_sidebar .hidden-sm table tbody tr"
        elif 'https://techspecs.ui.com/' in url:
            specs_selector = ".eGOVDM .egaTkP .hthDOj"
        elif 'https://store.ui.com/' in url:
            specs_selector = "#product-page .KdHGZ .JrttX .bHvGn .jjEjYH"
            button_to_click = "Technical Specification"
        else:
            return []

        await page.goto(url, wait_until="load", timeout=10000)
        await page.wait_for_load_state(state="networkidle")

        if button_to_click:
            try:
                await page.wait_for_selector("button", timeout=10000)
                buttons = await page.query_selector_all("button")

                for button in buttons:
                    text = await page.evaluate('(el) => el.textContent.trim()', button)
                    if button_to_click in text:
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
