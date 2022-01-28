"""Enable python -m khan_dl using the same console entry point."""
from . import main

if __name__ == '__main__':
    raise SystemExit(main())
