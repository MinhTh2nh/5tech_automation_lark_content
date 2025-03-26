import json

from app.helpers.formatter_image import download_image, upload_image

def wp_images_crawler_controller(original_list_url, image_alt_text, new_translate_post, is_5tech=False):
    try:
        original_list_url_array = json.loads(original_list_url)
        updated_translate_post = new_translate_post
        uploaded_urls = []

        for i, url in enumerate(original_list_url_array):
            new_file_name = f"{image_alt_text}-{i + 2}".replace(' ', '-').lower()
            image_data = download_image(url, new_file_name)

            if image_data['file_path']:
                alt_text = f"{image_alt_text} -{i + 2}"
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

        return {'uploaded_urls': uploaded_urls, 'updated_translate_post': updated_translate_post}
    except Exception as e:
        print(f"Error in wp_images_crawler_controller: {e}")
        return original_list_url