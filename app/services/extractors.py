async def extract_page_content(page, content_selector, unwanted_selectors):
    """Extract and clean text content from the page."""
    extracted_content = await page.evaluate('''(args) => {
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
    
    return extracted_content

async def extract_page_content_selector(page, content_selector, unwanted_selectors):
    """Extract and clean text content from the page."""
    extracted_content = await page.evaluate('''(args) => {
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
    
    return extracted_content

async def extract_page_content_selector(page, content_selector, unwanted_selectors):
    """Extract and clean text content from the page."""
    extracted_content = await page.evaluate('''(args) => {
        const [contentSelector, unwantedSelectors] = args;
        const element = document.querySelector(contentSelector);

        if (!element) return ''; // Return empty if no element found

        unwantedSelectors.forEach(selector => {
            element.querySelectorAll(selector).forEach(node => node.remove());
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

        return extractText(element).trim();
    }''', [content_selector, unwanted_selectors])
    
    return extracted_content
