import requests

def is_valid_download_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get('Content-Type', '')

        # Accept common downloadable formats
        if response.status_code == 200 and (
            'application/pdf' in content_type or
            'application/msword' in content_type or
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type
        ):
            return True
    except requests.RequestException:
        pass

    return False
