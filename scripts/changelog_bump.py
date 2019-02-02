import os
import re
import sys
from datetime import datetime
from typing import Match


LINK_REGEX = re.compile(r"\[(\w+)\](.*)(v.*)\.\.\.(.*)")


def update(
    content,
    match: Match,
    first_line: callable,
    second_line: callable,
    sep: str = "\n",
):
    assert match is not None
    line = content[match.start() : match.end()]
    return "".join(
        [
            content[: match.start()],
            sep.join([first_line(line), second_line(line)]),
            content[match.end() :],
        ]
    )


def bump_changelog(content: str, next_version: str):
    # Bump link references
    content = update(
        content,
        match=LINK_REGEX.search(content),
        first_line=lambda line: LINK_REGEX.sub(
            rf"[\g<1>]\g<2>{next_version}...\g<4>", line
        ),
        second_line=lambda line: LINK_REGEX.sub(
            rf"[{next_version}]\g<2>\g<3>...{next_version}", line
        ),
    )

    # Bump sections
    today = datetime.now().date()
    content = update(
        content,
        match=re.search(r"## \[Unreleased\]", content),
        first_line=lambda line: line,
        second_line=lambda line: f"## [{next_version}] - {today}",
        sep="\n\n",
    )

    return content


def main(path: str, next_version: str, debug=True):
    with open(path, "r") as f:
        out = bump_changelog(f.read(), next_version)
    if debug:
        print(out)
    else:
        with open(path, "w") as f:
            f.write(out)


def get_debug():
    try:
        sys.argv[2]
    except IndexError:
        return True
    else:
        return False


if __name__ == "__main__":
    main(
        os.path.join(os.getcwd(), "CHANGELOG.md"),
        next_version=sys.argv[1],
        debug=get_debug(),
    )
