import nox

Session = nox.sessions.Session


def _install_package(session: Session):
    session.install("-e", ".[full]")


@nox.session(reuse_venv=True)
def tests(session: Session):
    _install_package(session)
    session.install("pytest", "pytest-cov", "pytest-asyncio")
    if "coverage" in session.posargs and "missing" in session.posargs:
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


@nox.session(reuse_venv=True)
def docs(session: Session):
    _install_package(session)
    session.install("pydoc-markdown<2.0.5")
    session.run("pydocmd", "generate")
    if "serve" in session.posargs:
        session.run("vuepress", "dev", "docs", external=True)
    elif "api" not in session.posargs:
        session.run("vuepress", "build", "docs", external=True)


@nox.session(python=["3.6", "3.7"])
def ci(session: Session):
    session.install("codecov")
    tests(session)


@nox.session(reuse_venv=True)
def bumpversion(session: Session):
    session.install("bumpversion")
    session.run(
        "bash", "scripts/bumpversion.sh", *session.posargs, external=True
    )
