import os

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Vendor Configurations
# In a real app, this might come from a database or a YAML file.
VENDOR_CONFIGS = {
    "promos-ad-network": {
        "url": "https://httpbin.org/post",  # Using httpbin for testing
        "method": "POST",
        "headers_template": '{"Content-Type": "application/json", "X-Auth": "secret-key"}',
        "body_template": '{"event": "signup", "user_id": "{{ user_id }}", "source": "campaign"}'
    },
    "crm-system": {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "headers_template": '{"Authorization": "Bearer {{ token }}"}',
        "body_template": '{"contact_id": "{{ user_id }}", "status": "{{ status }}"}'
    },
    "inventory-system": {
        "url": "https://httpbin.org/put",
        "method": "PUT",
        "headers_template": '{"X-API-Key": "sku-123"}',
        "body_template": '{"sku": "{{ sku }}", "delta": {{ quantity * -1 }}}'
    }
}
