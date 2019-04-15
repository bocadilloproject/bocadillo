import re
import typing

PARAM_RE = re.compile(r"{}|{([a-zA-Z_:][a-zA-Z0-9_:]*)}")
WILDCARD = "{}"


def compile_path(pattern: str) -> typing.Tuple[typing.Pattern, str]:
    regex = "^"
    path_format = ""
    idx = 0

    for match in PARAM_RE.finditer(pattern):
        name, = match.groups(default="")
        if ":" in name:
            raise TypeError(
                "path specifiers were removed in 0.14.0. "
                "Use type annotations on view parameters instead, "
                "e.g. `pk: int` instead of '{pk:d}'"
            )

        regex += pattern[idx : match.start()]
        expr = r".+" if not name else rf"?P<{name}>[^/]+"
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
