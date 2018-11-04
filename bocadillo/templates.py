from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2 import Template as _Template

Template = _Template


def get_templates_environment(templates_dir: str):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html', 'xml']),
        enable_async=True,
    )
