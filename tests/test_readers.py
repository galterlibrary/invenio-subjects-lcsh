#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test readers."""

import datetime as dt
from pathlib import Path

from invenio_subjects_lcsh.filters import (
    deprecated_since_filter,
    non_geographic_filter,
    valid_heading_filter,
)
from invenio_subjects_lcsh.readers import LCSHMadsRdfJsonLdReader


def test_mads_rdf_json_ld_reader(valid_internal_entries):
    filepath = Path(__file__).parent / "data" / "fake_lcsh.madsrdf.jsonld"

    reader = LCSHMadsRdfJsonLdReader(
        filepath,
        filter=valid_heading_filter,
    )
    entries = list(reader.iter_internal_entries())

    assert valid_internal_entries == entries


def test_mads_rdf_json_ld_deprecated_of_interest_reader(
        deprecated_internal_entries
    ):
    # This is admittedly a conflation of testing concerns in order to
    # test the reader used in lcsh_replacements. We leave the proper
    # split of concerns for future work.
    filepath = Path(__file__).parent / "data" / "fake_lcsh.madsrdf.jsonld"

    reader = LCSHMadsRdfJsonLdReader(
        filepath,
        filter=lambda e: (
            non_geographic_filter(e)
            # Make sure that some "since-filtering" occurs by choosing a date
            # that will exclude one of the deprecated entries
            and deprecated_since_filter(e, dt.datetime(2023, 1, 1))
        ),
    )
    entries = list(reader.iter_internal_entries())

    # Exclude deprecated entry that should be filtered out from
    # deprecated_internal_entries
    expected = [
        e for e in deprecated_internal_entries
        if not e["deprecated"]["time"].startswith("2021-")
    ]
    assert expected == entries
