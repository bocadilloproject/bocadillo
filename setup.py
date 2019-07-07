"""Package setup."""

import setuptools

description = "Fast, highly-concurrent and scalable web APIs for everyone"

with open("README.md", "r") as readme:
    long_description = readme.read()

GITHUB = "https://github.com/bocadilloproject/bocadillo"
DOCS = "https://bocadilloproject.github.io"
CHANGELOG = f"{GITHUB}/blob/master/CHANGELOG.md"

INSTALL_REQUIRES = [
    "starlette>=0.12.2, <0.13",
    "uvicorn>=0.7, <0.9",
    "typesystem>=0.2.2",
    "jinja2>=2.10.1",
    "whitenoise",
    "requests",
    "python-multipart",
    "websockets>=6.0",
    "aiodine>=1.2.5, <2.0",
]

EXTRAS_REQUIRE = {"files": ["aiofiles"], "sessions": ["itsdangerous"]}
EXTRAS_REQUIRE["full"] = [
    req for reqs in EXTRAS_REQUIRE.values() for req in reqs
]

setuptools.setup(
    name="bocadillo",
    version="0.18.0",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.6",
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
)
