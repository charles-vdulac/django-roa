#!/usr/bin/env python
import os
import sys

# Add django_roa path:
django_roa_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../../../'
))
sys.path.insert(0, django_roa_path)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
