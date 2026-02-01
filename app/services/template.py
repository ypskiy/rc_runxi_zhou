from jinja2 import Template
import json

def render_payload(template_str: str, context: dict) -> dict:
    """
    Render a Jinja2 template string with the given context and parse it as JSON.
    Used for both Headers and Body.
    """
    try:
        # Render the template string using Jinja2
        rendered_str = Template(template_str).render(**context)
        
        # Parse the rendered string into a Python dictionary/list
        return json.loads(rendered_str)
    except json.JSONDecodeError as e:
        # If the template result isn't valid JSON, raise an error
        # Note: If headers_template is just a string, this will fail if it's not JSON formatted.
        # Our design assumes headers are defined as a JSON object in the template.
        raise ValueError(f"Rendered template is not valid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Template rendering error: {e}")
