# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import json
from pathlib import Path

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


def read_jsonl(filepath):
    """Read jsonl."""
    with open(filepath) as f:
        for line in f:
            yield json.loads(line)


def test_write():
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
    filepath = Path(__file__).parent / "test_lcsh_subjects.jsonl"

    LCSHWriter(entries).jsonl(filepath)

    read_entries = [e for e in read_jsonl(filepath)]
    assert entries == read_entries

    try:
        filepath.unlink()  # TODO: add missing_ok=True starting python 3.8+
    except FileNotFoundError:
        pass
