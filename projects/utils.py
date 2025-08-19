# utils.py
import requests

# Checks if a given URL is a valid download link for a supported document type
def is_valid_download_link(url): 
    try:
        # Send a HEAD request to the URL to get headers, following redirects and with a timeout
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Get the Content-Type header from the response (default to empty string if missing)
        content_type = response.headers.get('Content-Type', '')

        # Return True only if:
        # - The server responds with HTTP 200 OK
        # - The content type is PDF, MS Word (.doc), or Word (.docx)
        if response.status_code == 200 and (
            'application/pdf' in content_type or
            'application/msword' in content_type or
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type
        ):
            return True
    # If any requests-related exception occurs, ignore and continue
    except requests.RequestException:
        pass

    # If checks failed or an exception occurred, return False
    return False