"""Khan Academy course downloader; importing it performs no network work."""

__version__ = "1.1.0"


def main(argv=None):
    from .cli import main as cli_main
    return cli_main(argv)
