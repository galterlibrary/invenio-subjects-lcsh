# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Command line tool."""

from pathlib import Path

import click

from invenio_subjects_lcsh.extractor import LCSHExtractor
from invenio_subjects_lcsh.writer import LCSHWriter


@click.command()
def main():
    """Generate new subjects_lcsh.yaml file."""
    current_dir = Path(__file__).parent
    # Assume file is in download/
    filepath = current_dir / "download/subjects.skosrdf.jsonld"

    extractor = LCSHExtractor(filepath)

    output_filepath = current_dir / "vocabularies/subjects_lcsh.yaml"
    LCSHWriter(extractor).yaml(output_filepath)

    print(f"LCSH terms have been written here {output_filepath}")
