"""``python -m piensalo`` entry point — delegates to the CLI."""
from piensalo.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
