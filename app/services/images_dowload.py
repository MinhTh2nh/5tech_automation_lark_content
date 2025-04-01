import json
import unicodedata
import re
from app.helpers.formatter_image import download_image, upload_image
def remove_accents(text):
    """Remove accents from text using built-in unicodedata."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)
    )

def sanitize_filename(text):
    """Sanitize filenames: Remove accents, replace spaces with dashes, and remove special characters."""
    text = remove_accents(text)  # Convert accented characters to ASCII
    text = text.lower().replace(" ", "-")  # Replace spaces with dashes
    text = re.sub(r"[^a-z0-9-]", "", text)  # Remove special characters except dashes
    return text
def wp_images_crawler_controller(list_of_items, is_5tech=False):
    try:
        results = []
        for item in list_of_items:
            original_list_url = item.get("list_of_featured_images")
            craw_content_blog = item.get("craw_content_blog", [])
            updated_translate_post = craw_content_blog[0].get("translatedText") if craw_content_blog else ""
            raw_post_title = item.get("post_title", "").strip()

            craw_data_technical_specification = item.get("craw_data_technical_specification", [])
            meta_yoast_wpseo_focuskw = item.get("meta:_yoast_wpseo_focuskw", [])
            meta_yoast_wpseo_metadesc = item.get("meta:_yoast_wpseo_metadesc", [])
            meta_yoast_wpseo_title = item.get("meta:_yoast_wpseo_title", [])
            sku = item.get("sku", [])

            image_alt_text = sanitize_filename(raw_post_title)
            uploaded_urls = []

            for i, url in enumerate(original_list_url):
                new_file_name = f"{image_alt_text}-{i + 2}".replace(' ', '-').lower()
                image_data = download_image(url, new_file_name)

                if image_data and image_data.get('file_path'):
                    alt_text = f"{image_alt_text} - {i + 2}"
                    uploaded_url = upload_image(
                        image_data=image_data, 
                        alt_text=alt_text, 
                        is_5tech=is_5tech
                    )
                    if uploaded_url and updated_translate_post:
                        updated_translate_post = updated_translate_post.replace(url, uploaded_url)
                    uploaded_urls.append(uploaded_url or url)
                else:
                    uploaded_urls.append(url)
            print("Finished uploading images for post:", raw_post_title)
            results.append({
                'uploaded_urls': uploaded_urls, 
                'updated_translate_post': updated_translate_post, 
                'post_title': raw_post_title,
                'craw_data_technical_specification': craw_data_technical_specification,
                'meta_yoast_wpseo_focuskw': meta_yoast_wpseo_focuskw,
                'meta_yoast_wpseo_metadesc': meta_yoast_wpseo_metadesc,
                'meta_yoast_wpseo_title': meta_yoast_wpseo_title,
                'sku': sku,
                'image_alt_text': image_alt_text,
            })


        return results
    except Exception as e:
        print(f"Error in wp_images_crawler_controller: {e}")
        return original_list_url
    

def wp_images_crawler_controller_content(original_list_url, image_alt_text, new_translate_post, is_5tech=False):
    try:
        original_list_url_array = json.loads(original_list_url)
        updated_translate_post = new_translate_post
        uploaded_urls = []

        for i, url in enumerate(original_list_url_array):
            if url.startswith(("data://", "images://")):
                continue 

            new_file_name = f"{image_alt_text}-{i + 2}".replace(' ', '-').lower()
            image_data = download_image(url, new_file_name)

            if image_data and image_data.get('file_path'):
                alt_text = f"{image_alt_text} -{i + 2}"
                uploaded_url = upload_image(
                    image_data=image_data, 
                    alt_text=alt_text, 
                    is_5tech=is_5tech
                )

                if uploaded_url and uploaded_url.startswith("https://connect.quik.vn"):
                    uploaded_urls.append(uploaded_url)
                    if updated_translate_post:
                        updated_translate_post = updated_translate_post.replace(url, uploaded_url)

        return {'uploaded_urls': uploaded_urls, 'updated_translate_post': updated_translate_post}

    except Exception as e:
        print(f"Error in wp_images_crawler_controller_content: {e}")
        return {'uploaded_urls': [], 'updated_translate_post': new_translate_post}