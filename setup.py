"""Build metadata; importing the package is deliberately unnecessary here."""
from pathlib import Path
import re
from setuptools import setup

HERE = Path(__file__).parent
VERSION = re.search(r'__version__ = "([^"]+)"',
                    (HERE / 'khan_dl' / '__init__.py').read_text(encoding='utf-8')).group(1)

setup(
    name='khan-dl',
    version=VERSION,
    description='Download public Khan Academy courses, audio and subtitles',
    long_description=(HERE / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url='https://github.com/imsakg/khan-dl',
    author='rand-net',
    license='MIT',
    python_requires='>=3.8',
    classifiers=['License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3 :: Only'],
    packages=['khan_dl'],
    include_package_data=True,
    entry_points={'console_scripts': ['khan-dl = khan_dl:main']},
    install_requires=['beautifulsoup4>=4.9.3', 'requests>=2.25.1',
                      'youtube-dl>=2021.12.17', 'fuzzywuzzy>=0.18.0'],
    extras_require={'interactive': ['prompt-toolkit>=3.0.14'],
                    'dev': ['build>=0.7', 'wheel']},
    keywords=['khan academy', 'course downloader', 'audio', 'subtitles'],
)
