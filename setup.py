# Built-in imports
from pathlib import Path

# Third-party imports
from setuptools import setup, find_packages

# Local imports
from streamsnapper import __version__, __license__


setup(
    name='streamsnapper',
    version=__version__,
    description='StreamSnapper is an intuitive library designed to simplify and enhance YouTube media downloads. It offers efficient, high-speed media extraction with optional tools for advanced data retrieval from YouTube.',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/henrique-coder/streamsnapper',
    author='henrique-coder',
    author_email='hjyz6rqyb@mozmail.com',
    license=__license__,
    packages=find_packages(),
    install_requires=[
        'pysmartdl2',
        'scrapetube',
        'yt-dlp'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    python_requires='>=3.12'
)
