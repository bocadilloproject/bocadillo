import re
import typing

PARAM_RE = re.compile(r"{}|{([a-zA-Z_:][a-zA-Z0-9_:]*)}")
WILDCARD = "{}"

CONVERTER_PATTERNS = {"path": r".*"}


def convert_part(name: str, converter: str) -> str:
    try:
        return CONVERTER_PATTERNS[converter]
    except KeyError as exc:
        raise TypeError(
            f"Unknown path converter '{converter}' "
            f"on route parameter '{name}'. "
            f"Available: {', '.join(CONVERTER_PATTERNS)}"
        ) from exc


def compile_path(pattern: str) -> typing.Tuple[typing.Pattern, str]:
    regex = "^"
    path_format = ""
    idx = 0

    for match in PARAM_RE.finditer(pattern):
        declaration, = match.groups(default="")
        name, sep, converter = declaration.partition(":")
        has_converter = sep == ":"

        regex += pattern[idx : match.start()]
        if not name:
            expr = r".*"
        else:
            part = convert_part(name, converter) if has_converter else r"[^/]+"
            expr = rf"?P<{name}>{part}"
        regex += rf"({expr})"

        path_format += pattern[idx : match.start()]
        path_format += "{%s}" % name

        idx = match.end()

    regex += pattern[idx:] + "$"
    path_format += pattern[idx:]

    return re.compile(regex), path_format


class Parser:
    def __init__(self, pattern: str):
        if pattern != WILDCARD and not pattern.startswith("/"):
            pattern = f"/{pattern}"
        self.regex, self.pattern = compile_path(pattern)

    def parse(self, value: str) -> typing.Optional[dict]:
        match = self.regex.match(value)
        if match is None:
            return None
        return match.groupdict()
