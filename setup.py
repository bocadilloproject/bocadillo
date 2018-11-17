"""Package setup."""

import setuptools

description = (
    'A modern Python web framework filled with asynchronous salsa.'
)

with open('README.md', 'r') as readme:
    long_description = readme.read()


setuptools.setup(
    name='bocadillo',
    version='0.5.0',
    author='Florimond Manca',
    author_email='florimond.manca@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['bocadillo', 'bocadillo.ext'],
    install_requires=[
        'starlette',
        'uvicorn',
        'jinja2',
        'asgiref',
        'whitenoise',
        'requests',
        'parse',
    ],
    url='https://github.com/bocadilloproject/bocadillo',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    entry_points={
        'console_scripts': [
            'boca=bocadillo.cli:cli',
        ]
    },
)
