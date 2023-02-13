#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import debugpy
from django.conf import settings


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

    if settings.DEBUG:
        if (
            os.environ.get("RUN_MAIN")
            or os.environ.get("WERKZEUG_RUN_MAIN")
            and sys.argv[1] == "runserver"
        ):
            import debugpy

            debugpy.listen(("0.0.0.0", 3000))
            print("Attached!")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()