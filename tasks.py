# Copyright (C) 2023-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from invoke import task


@task
def test(c, color=True, passthru=""):
    """Run tests."""
    c.run(f"python -m pytest {passthru}", pty=color)


@task
def clean(c):
    """Clean."""
    c.run("rm -rf *.egg-info/ */*.egg-info/ dist/ build/")
