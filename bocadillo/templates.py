from typing import List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2 import Template as _Template

Template = _Template


def get_templates_environment(template_dirs: List[str]):
    return Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=select_autoescape(['html', 'xml']),
        enable_async=True,
    )
