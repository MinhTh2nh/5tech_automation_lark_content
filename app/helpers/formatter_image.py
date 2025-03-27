import requests
import os
from pathlib import Path

WP_UPLOAD_URL = 'https://connect.quik.vn/wp-json/wp/v2/media'

AUTH = {
    'username': 'ThanhNM',
    'password': '1ODx xS9B 2tAd fYi1 ic2x jvRz'
}

WP_UPLOAD_URL_5TECH = 'https://5tech.com.vn/wp-json/wp/v2/media'

AUTH_5TECH = {
    'username': 'ThanhNM',
    'password': 'LdnB jt9i C2JQ bUHf qWYM wwMq'
}

def is_valid_image_type(content_type):
    """Check if the content type is a valid image type."""
    return content_type and content_type.startswith('image/')

def download_image(url, new_file_name):
    """Download an image from a URL and save it locally."""
    try:
        if not url.startswith(('http://', 'https://')):
            return {'file_path': None, 'content_type': None, 'old_url': url}
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('content-type')

        if not is_valid_image_type(content_type):
            return {'file_path': None, 'content_type': None, 'old_url': url}

        ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
        new_file_path = os.path.join(os.getcwd(), f"{new_file_name}{ext}")

        with open(new_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {
            'file_path': new_file_path,
            'content_type': content_type or 'image/jpeg',
            'old_url': url
        }
    except Exception as e:
        return {'file_path': None, 'content_type': None, 'old_url': url}

def upload_image(image_data, alt_text, is_5tech):
    """Upload an image to WordPress and return the source URL."""
    try:
        file_path = image_data["file_path"]
        content_type = image_data["content_type"]

        wp_url = WP_UPLOAD_URL_5TECH if is_5tech else WP_UPLOAD_URL
        auth = AUTH_5TECH if is_5tech else AUTH

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, content_type)}
            data = {"alt_text": alt_text.encode("utf-8")}
            headers = {
                "Content-Disposition": f'attachment; filename="{os.path.basename(file_path)}"'
            }
            response = requests.post(wp_url, auth=(auth["username"], auth["password"]), files=files, data=data, headers=headers)
            response.raise_for_status()

        os.unlink(file_path)
        return response.json()["source_url"]

    except requests.exceptions.RequestException as e:
        if e.response:
            print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

