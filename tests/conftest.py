#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Conftest."""

import pytest


@pytest.fixture()
def valid_internal_entries():
    """Fixture for valid LCSH internal entries."""
    return [
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2006005259",
            "label": "Video games industry",
            "deprecated": {
                "status": False,
                "note": "",
                "replacements": [],
                "time": "",
            },
            "collections": [
                "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_LCSH_General",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_SubdivideGeographically",  # noqa
            ],
        },
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2021004026",
            "label": "Child internment camp inmates",
            "deprecated": {
                "status": False,
                "note": "",
                "replacements": [],
                "time": "",
            },
            "collections": [
                "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_LCSH_General",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_SubdivideGeographically",  # noqa
            ],
        },
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2021004027",
            "label": "Child Nazi concentration camp inmates",
            "deprecated": {
                "status": False,
                "note": "",
                "replacements": [],
                "time": "",
            },
            "collections": [
                "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_LCSH_General",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_SubdivideGeographically",  # noqa
            ],
        },
        {
            "id": "http://id.loc.gov/authorities/subjects/sh85143203",
            "label": "Video games--Law and legislation",
            "deprecated": {
                "status": False,
                "note": "",
                "replacements": [],
                "time": "",
            },
            "collections": [
                "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_LCSH_General",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_SubdivideGeographically",  # noqa
            ],
        },
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2022001319",
            "label": "Evangelisch Luthersche Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "deprecated": {
                "status": False,
                "note": "",
                "replacements": [],
                "time": "",
            },
            "collections": [
                "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",  # noqa
                "http://id.loc.gov/authorities/subjects/collection_LCSH_General",  # noqa
            ],
        },
    ]

@pytest.fixture()
def deprecated_internal_entries():
    return [
        # Single new_id/new_subject
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2008007279",
            "label": "Computer games industry",
            "deprecated": {
                "status": True,
                "note": "This authority record has been deleted because the heading is covered by the subject heading {Video games industry} (DLC)sh2006005259",  # noqa
                "replacements": [
                    "http://id.loc.gov/authorities/subjects/sh2006005259",
                ],
                "time": "2023-01-23T12:01:15",
            },
            "collections": [],
        },
        # Multiple potential new_id's/new_subject's - curator intervention
        # will be needed
        {
            "id": "http://id.loc.gov/authorities/subjects/sh00000273",
            "label": "Child concentration camp inmates",
            "deprecated": {
                "status": True,
                "note": "This authority record has been deleted because the heading is covered by the subject headings {Child internment camp inmates} (DLC)sh2021004026 and {Child Nazi concentration camp inmates} (DLC)sh2021004027",  # noqa
                "replacements": [
                    "http://id.loc.gov/authorities/subjects/sh2021004026",
                    "http://id.loc.gov/authorities/subjects/sh2021004027",
                ],
                "time": "2021-07-20T08:25:20",
            },
            "collections": [],
        },
        # Variation: strange formatting in notes
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2006004185",
            "label": "Computer games--Law and legislation",
            "deprecated": {
                "status": True,
                "note": "This authority record has been deleted because the heading is covered by the subject heading {Video games--Law and legislation} (DLC)sh 85143203",  # noqa
                "replacements": [
                    "http://id.loc.gov/authorities/subjects/sh85143203",
                ],
                "time": "2023-01-23T12:01:15",
            },
            "collections": [],
        },
        # Variation: different wording + no replacement subject in notes
        {
            "id": "http://id.loc.gov/authorities/subjects/sh2022001344",
            "label": "Evangelisch-Lutherse Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "deprecated": {
                "status": True,
                "note": "This authority record has been deleted because the heading is covered by an identical subject heading (DLC)sh2022001319",  # noqa
                "replacements": [
                    "http://id.loc.gov/authorities/subjects/sh2022001319",
                ],
                "time": "2023-09-29T18:42:32",
            },
            "collections": [],
        },
        # Variation: LCNAF replacement
        {
            "id": "http://id.loc.gov/authorities/subjects/sh98006437",
            "label": "Calvin (Fictitious character : Watterson)",  # noqa
            "deprecated": {
                "status": True,
                "note": "This authority record has been deleted because the subject heading is covered by the name heading {Calvin (Fictitious character from Watterson)} (DLC)no2020114212",  # noqa
                "replacements": [
                    "http://id.loc.gov/authorities/names/no2020114212",
                ],
                "time": "2026-05-27T13:37:37",
            },
            "collections": [],
        },
    ]
