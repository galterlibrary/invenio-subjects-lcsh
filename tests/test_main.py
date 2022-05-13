# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from pathlib import Path

import yaml

from invenio_subjects_lcsh.extractor import LCSHExtractor
from invenio_subjects_lcsh.writer import LCSHWriter


def test_lcsh_extractor():
    # File is setup to test
    # - regular entries
    # - deprecated entry that is ignored
    # - entry with multiple labels (take the last)
    filepath = Path(__file__).parent / "data" / "fake_lcsh_subjects.jsonld"
    extractor = LCSHExtractor(filepath)

    expected = [e for e in extractor]

    received = [
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00000011',
            "scheme": "LCSH",
            "subject": "ActionScript (Computer program language)"
        },
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00000014',
            "scheme": "LCSH",
            "subject": "Tacos"
        },
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh90000997',
            "scheme": "LCSH",
            "subject": "Rooms"
        }

    ]
    assert expected == received


def test_write():
    filepath = Path(__file__).parent / "test_lcsh_subjects.yaml"
    entries = [
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00000011',
            "scheme": "LCSH",
            "subject": "ActionScript (Computer program language)"
        },
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00000014',
            "scheme": "LCSH",
            "subject": "Tacos"
        },
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00000275',
            "scheme": "LCSH",
            "subject": "Shell Lake (Wis. : Lake)"
        },
        {
            "id": 'http://id.loc.gov/authorities/subjects/sh00008126',
            "scheme": "LCSH",
            "subject": "Half-Circle \"V\" Ranch (Wyo.)"
        },
    ]

    LCSHWriter(entries).yaml(filepath)

    with open(filepath) as f:
        read_entries = yaml.safe_load(f)
    assert entries == read_entries

    try:
        filepath.unlink()  # TODO: add missing_ok=True starting python 3.8+
    except FileNotFoundError:
        pass
