"""Package setup."""

import setuptools

description = "A modern Python web framework filled with asynchronous salsa."

with open("README.md", "r") as readme:
    long_description = readme.read()

GITHUB = "https://github.com/bocadilloproject/bocadillo"
DOCS = "https://bocadilloproject.github.io"
CHANGELOG = f"{GITHUB}/blob/master/CHANGELOG.md"

setuptools.setup(
    name="bocadillo",
    version="0.10.1",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["bocadillo", "bocadillo.scaffold"],
    package_data={"bocadillo": ["assets/*"]},
    install_requires=[
        "starlette",
        "uvicorn>=0.3.26",
        "jinja2",
        "whitenoise",
        "requests",
        "parse",
        "websockets>=6.0",
    ],
    url=DOCS,
    project_urls={
        "Source": GITHUB,
        "Documentation": DOCS,
        "Changelog": CHANGELOG,
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    entry_points={"console_scripts": ["boca=bocadillo.__main__:cli"]},
)
