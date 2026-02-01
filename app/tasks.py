import requests
import logging
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential_jitter, 
    retry_if_exception_type,
    before_sleep_log
)
from app.config import VENDOR_CONFIGS
from app.services.template import render_payload
# from app.utils.logger import setup_logger

logger = logging.getLogger("rq.worker") # Use RQ's logger or standard one

# Define custom exceptions
class RecoverableError(Exception):
    pass

class PermanentError(Exception):
    pass

# Retry Strategy
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=60, jitter=1),
    retry=retry_if_exception_type((requests.RequestException, RecoverableError)),
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.WARN)
)
def deliver_notification(vendor_id: str, context: dict):
    config = VENDOR_CONFIGS.get(vendor_id)
    if not config:
        # Configuration error is permanent
        raise PermanentError(f"Configuration missing for vendor {vendor_id}")

    # 1. Template Rendering
    try:
        url = config['url']
        method = config['method']
        # Render Headers
        headers_template = config.get('headers_template', '{}')
        headers = render_payload(headers_template, context) if headers_template else {}
        
        # Render Body
        body_template = config.get('body_template', '{}')
        body = render_payload(body_template, context) if body_template else {}
        
    except Exception as e:
        logger.error(f"Template rendering failed: {e}")
        # Template errors are usually permanent (bad data or bad template)
        raise PermanentError(f"Templating Error: {e}")

    # 2. HTTP Request
    try:
        logger.info(f"Sending request to {url} for vendor {vendor_id}")
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body,
            timeout=(3.05, 10)  # Connect timeout, Read timeout
        )
        
        # 3. Response Handling
        if response.status_code < 400:
            logger.info(f"Notification delivered successfully. Status: {response.status_code}")
            return response.json()
        
        # 429 Too Many Requests -> Retry
        if response.status_code == 429:
            logger.warning("Rate limited by vendor.")
            raise RecoverableError("Rate Limited")
        
        # 5xx Server Errors -> Retry
        if 500 <= response.status_code < 600:
            logger.warning(f"Vendor server error: {response.status_code}")
            raise RecoverableError(f"Server Error {response.status_code}")
        
        # 4xx Client Errors -> Permanent Fail
        if 400 <= response.status_code < 500:
            logger.error(f"Client Error (Not Retrying): {response.status_code} - {response.text}")
            raise PermanentError(f"Client Error {response.status_code}")

    except requests.RequestException as e:
        # Network errors -> Retry
        logger.warning(f"Network exception: {e}")
        raise e
