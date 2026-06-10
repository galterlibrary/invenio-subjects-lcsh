# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from datetime import datetime
from pathlib import Path

import pytest
from galter_subjects_utils.reader import read_jsonl

from invenio_subjects_lcsh.converter import LCSHRDMConverter
from invenio_subjects_lcsh.mads_rdf_jsonld import (
    enhance_replacements_w_new_subjects,
    topics_to_replacements,
)


@pytest.fixture
def topics_lcsh():
    """Function scoped list of LCSH topics as read from bulk download.

    fake_lcsh.madsrdf.jsonld adds the
    "@https://github.com/galterlibrary/invenio-subjects-lcsh" key to indicate
    the test role of the entry (e.g. a regular entry, a deprecated one).
    This key is not present in a real lcsh.madsrdf.jsonld entry but helps
    when reading the file to understand the purpose of each entry.
    """
    filepath = Path(__file__).parent / "data" / "fake_lcsh.madsrdf.jsonld"
    topics = list(read_jsonl(filepath))
    return topics


def test_converter(topics_lcsh):
    converter = LCSHRDMConverter(topics_lcsh)

    dicts_of_lcsh_terms = [d for d in converter.convert()]

    expected = [
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2006005259",
            "scheme": "LCSH",
            "subject": "Video games industry",
        },
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2021004026",
            "scheme": "LCSH",
            "subject": "Child internment camp inmates",
        },
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2021004027",
            "scheme": "LCSH",
            "subject": "Child Nazi concentration camp inmates",
        },
        {
            "id": "https://id.loc.gov/authorities/subjects/sh85143203",
            "scheme": "LCSH",
            "subject": "Video games--Law and legislation",
        },
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2022001319",
            "scheme": "LCSH",
            "subject": "Evangelisch Luthersche Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
        },
    ]
    assert expected == dicts_of_lcsh_terms


def test_deprecated(topics_lcsh):
    replacements = topics_to_replacements(topics_lcsh)
    replacements = enhance_replacements_w_new_subjects(
        replacements, topics_lcsh
    )
    replacements = list(replacements)

    expected = [
        # Single new_id/new_subject
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2008007279",
            "time": "2023-01-23T12:01:15",
            "subject": "Computer games industry",
            "new_id": "https://id.loc.gov/authorities/subjects/sh2006005259",
            "new_subject": "Video games industry",
            "notes": "This authority record has been deleted because the heading is covered by the subject heading {Video games industry} (DLC)sh2006005259",  # noqa
        },
        # Multiple potential new_id's/new_subject's - curator intervention
        # will be needed
        {
            "id": "https://id.loc.gov/authorities/subjects/sh00000273",
            "time": "2021-07-20T08:25:20",
            "subject": "Child concentration camp inmates",
            "new_id": "https://id.loc.gov/authorities/subjects/sh2021004026\nhttps://id.loc.gov/authorities/subjects/sh2021004027",  # noqa
            "new_subject": "Child internment camp inmates\nChild Nazi concentration camp inmates",  # noqa
            "notes": "This authority record has been deleted because the heading is covered by the subject headings {Child internment camp inmates} (DLC)sh2021004026 and {Child Nazi concentration camp inmates} (DLC)sh2021004027",  # noqa
        },
        # Variation: strange formatting in notes to account for
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2006004185",
            "time": "2023-01-23T12:01:15",
            "subject": "Computer games--Law and legislation",
            "new_id": "https://id.loc.gov/authorities/subjects/sh85143203",
            "new_subject": "Video games--Law and legislation",
            "notes": "This authority record has been deleted because the heading is covered by the subject heading {Video games--Law and legislation} (DLC)sh 85143203",  # noqa
        },
        # Variation: different wording + no replacement subject in notes
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2022001344",
            "time": "2023-09-29T18:42:32",
            "subject": "Evangelisch-Lutherse Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "new_id": "https://id.loc.gov/authorities/subjects/sh2022001319",
            "new_subject": "Evangelisch Luthersche Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "notes": "This authority record has been deleted because the heading is covered by an identical subject heading (DLC)sh2022001319",  # noqa
        },
    ]
    assert expected == replacements


def test_deprecated_since(topics_lcsh):
    replacements = topics_to_replacements(
        topics_lcsh,
        since=datetime(2023, 9, 29)
    )
    replacements = enhance_replacements_w_new_subjects(
        replacements, topics_lcsh
    )
    replacements = list(replacements)

    expected = [
        {
            "id": "https://id.loc.gov/authorities/subjects/sh2022001344",
            "time": "2023-09-29T18:42:32",
            "subject": "Evangelisch-Lutherse Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "new_id": "https://id.loc.gov/authorities/subjects/sh2022001319",
            "new_subject": "Evangelisch Luthersche Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "notes": "This authority record has been deleted because the heading is covered by an identical subject heading (DLC)sh2022001319",  # noqa
        },
    ]
    assert expected == replacements
