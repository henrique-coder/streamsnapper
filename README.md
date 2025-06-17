## StreamSnapper

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Code Style](https://img.shields.io/badge/code%20style-ruff-blue?style=flat&logo=ruff&logoColor=blue&color=blue&link=https://github.com/astral-sh/ruff)
![PyPI - Format](https://img.shields.io/pypi/format/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Python Compatible Versions](https://img.shields.io/pypi/pyversions/streamsnapper?style=flat&logo=python&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)

StreamSnapper is an intuitive library designed to simplify, improve, and organize YouTube and Youtube Music media streams. It offers scraping functions with higher speed extraction and efficiency with the latest tools to perform such processes.

#### Installation (from [PyPI](https://pypi.org/project/streamsnapper))

```bash
# Install the stable version of StreamSnapper from PyPI (recommended)
pip install --upgrade streamsnapper

# Install the development version of StreamSnapper from GitHub
pip install --upgrade git+https://github.com/henrique-coder/streamsnapper.git@main
```

> [!Note]
> If you already have a version installed and want to switch to a different branch (for example, to test new features or fix bugs), you will need to use the `--force-reinstall` parameter to ensure the upgrade occurs correctly.

### Example Usage

```python
from streamsnapper import YouTube


youtube = YouTube(logging=False, cookies=None)
youtube.extract(url="https://www.youtube.com/watch?v=***********", ytdlp_data=None)
youtube.analyze_information(check_thumbnails=False, retrieve_dislike_count=False)
youtube.analyze_video_streams(preferred_quality="all")
youtube.analyze_audio_streams(preferred_language="source")
youtube.analyze_subtitle_streams()

print(youtube.information.to_dict())
print(youtube.best_video_stream)
print(youtube.best_audio_stream)
print(youtube.subtitle_streams)

# And much more useful classes and functions

```

### Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, fork the repository and create a pull request. You can also simply open an issue and describe your ideas or report bugs. **Don't forget to give the project a star if you like it!**

1. Fork the project;
2. Create your feature branch ・ `git checkout -b feature/{feature_name}`;
3. Commit your changes ・ `git commit -m "{commit_message}"`;
4. Push to the branch ・ `git push origin feature/{feature_name}`;
5. Open a pull request, describing the changes you made and wait for a review.

### Disclaimer

Please note that downloading copyrighted content from some media services may be illegal in your country. This tool is designed for educational purposes only. Use at your own risk.
