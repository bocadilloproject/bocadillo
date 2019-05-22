import os

import nox

Session = nox.sessions.Session
VUEPRESS = os.path.join(".", "node_modules", "vuepress", "bin", "vuepress.js")


@nox.session(reuse_venv=True)
def test(session: Session):
    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov", "pytest-asyncio")
    if "coverage:missing" in session.posargs:
        session.run(
            "pytest",
            "--cov=./",
            "--cov-report",
            "term:skip-covered",
            "--cov-report",
            "term-missing",
        )
    elif "coverage" in session.posargs:
        session.run("pytest", "--cov=./")
    else:
        session.run("pytest")


@nox.session(python=["3.6", "3.7"])
def ci(session: Session):
    session.install("codecov")
    test(session)


@nox.session(reuse_venv=True)
def bumpversion(session: Session):
    session.install("bumpversion")
    session.run(
        "bash", "scripts/bumpversion.sh", *session.posargs, external=True
    )
