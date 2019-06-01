from invoke import task


@task
def install(c):
    c.run("pip install -r requirements.txt")
    c.run("pre-commit install")


@task
def test(c):
    c.run("pytest")


@task
def coverage(c, missing=False):
    command = "pytest --cov=bocadillo tests/ --cov-fail-under=100"
    if missing:
        command += " --cov-report term-missing --cov-report term:skip-covered"
    c.run(command)


@task
def ci(c):
    c.run("pip install codecov")
    coverage(c)


@task
def apiref(c):
    c.run("pydocmd generate")


@task
def bumpversion(c, level):
    c.run("pip install bumpversion")
    c.run(f"bash scripts/bumpversion.sh {level}")
