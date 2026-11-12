#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test converters."""

from pathlib import Path

from galter_subjects_utils.reader import read_csv

from invenio_subjects_lcsh.converters import (
    LCSHRDMConverter,
    LCSHReplacementConverter,
)


def test_rdm_converter(valid_internal_entries):
    converter = LCSHRDMConverter(valid_internal_entries)

    dicts_of_lcsh_terms = [d for d in converter.iter_rdm_subjects()]

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


def test_replacement_converter(deprecated_internal_entries):
    filepath_subjects_lcsh = Path(__file__).parent / "data" / "fake_subjects_lcsh.csv"  # noqa

    sources_for_new_subject_labels = [
        read_csv(filepath_subjects_lcsh),
    ]

    converter = LCSHReplacementConverter(
        deprecated_internal_entries,
        sources_for_new_subject_labels,
    )

    replacements, _ = converter.iter_replacements()
    replacements = list(replacements)

    expected = [
        # Single new_id/new_subject
        {
            "time": "2023-01-23T12:01:15",
            "id_src": "https://id.loc.gov/authorities/subjects/sh2008007279",
            "scheme_src": "LCSH",
            "subject_src": "Computer games industry",
            "id_dst": "https://id.loc.gov/authorities/subjects/sh2006005259",
            "scheme_dst": "LCSH",
            "subject_dst": "Video games industry",
            "notes": "This authority record has been deleted because the heading is covered by the subject heading {Video games industry} (DLC)sh2006005259",  # noqa
        },
        # Multiple potential new_id's/new_subject's - curator intervention
        # will be needed
        {
            "time": "2021-07-20T08:25:20",
            "id_src": "https://id.loc.gov/authorities/subjects/sh00000273",
            "scheme_src": "LCSH",
            "subject_src": "Child concentration camp inmates",
            "id_dst": "https://id.loc.gov/authorities/subjects/sh2021004026\nhttps://id.loc.gov/authorities/subjects/sh2021004027",  # noqa
            "scheme_dst": "LCSH\nLCSH",
            "subject_dst": "Child internment camp inmates\nChild Nazi concentration camp inmates",  # noqa
            "notes": "This authority record has been deleted because the heading is covered by the subject headings {Child internment camp inmates} (DLC)sh2021004026 and {Child Nazi concentration camp inmates} (DLC)sh2021004027",  # noqa
        },
        # Variation: strange formatting in notes to account for
        {
            "time": "2023-01-23T12:01:15",
            "id_src": "https://id.loc.gov/authorities/subjects/sh2006004185",
            "scheme_src": "LCSH",
            "subject_src": "Computer games--Law and legislation",
            "id_dst": "https://id.loc.gov/authorities/subjects/sh85143203",
            "scheme_dst": "LCSH",
            "subject_dst": "Video games--Law and legislation",
            "notes": "This authority record has been deleted because the heading is covered by the subject heading {Video games--Law and legislation} (DLC)sh 85143203",  # noqa
        },
        # Variation: different wording + no replacement subject in notes
        {
            "time": "2023-09-29T18:42:32",
            "id_src": "https://id.loc.gov/authorities/subjects/sh2022001344",
            "scheme_src": "LCSH",
            "subject_src": "Evangelisch-Lutherse Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "id_dst": "https://id.loc.gov/authorities/subjects/sh2022001319",
            "scheme_dst": "LCSH",
            "subject_dst": "Evangelisch Luthersche Kerk (Netherlands)--Relations--Nederlandse Hervormde Kerk",  # noqa
            "notes": "This authority record has been deleted because the heading is covered by an identical subject heading (DLC)sh2022001319",  # noqa
        },
        # Variation: LCNAF replacement but no LCNAF source
        {
            "time": "2026-05-27T13:37:37",
            "id_src": "https://id.loc.gov/authorities/subjects/sh98006437",
            "scheme_src": "LCSH",
            "subject_src": "Calvin (Fictitious character : Watterson)",
            "id_dst": "https://id.loc.gov/authorities/names/no2020114212",
            "scheme_dst": "LCNAF",
            "subject_dst": "",  # because no LCNAF source
            "notes": "This authority record has been deleted because the subject heading is covered by the name heading {Calvin (Fictitious character from Watterson)} (DLC)no2020114212",  # noqa
        },
    ]
    assert expected == replacements


def test_replacement_converter_w_lcnaf(deprecated_internal_entries):
    filepath_subjects_lcsh = (
        Path(__file__).parent / "data" / "fake_subjects_lcsh.csv"
    )
    filepath_subjects_lcnaf = (
        Path(__file__).parent / "data" / "fake_subjects_lcnaf.csv"
    )
    sources_for_new_subject_labels = [
        read_csv(filepath_subjects_lcsh),
        read_csv(filepath_subjects_lcnaf),
    ]

    converter = LCSHReplacementConverter(
        deprecated_internal_entries,
        sources_for_new_subject_labels,
    )

    replacements, _ = converter.iter_replacements()
    replacements = list(replacements)

    expected = {
        "time": "2026-05-27T13:37:37",
        "id_src": "https://id.loc.gov/authorities/subjects/sh98006437",
        "scheme_src": "LCSH",
        "subject_src": "Calvin (Fictitious character : Watterson)",
        "id_dst": "https://id.loc.gov/authorities/names/no2020114212",
        "scheme_dst": "LCNAF",
        # Filled because do have an LCNAF labelling source
        "subject_dst": "Calvin (Fictitious character : Watterson)",
        "notes": "This authority record has been deleted because the subject heading is covered by the name heading {Calvin (Fictitious character from Watterson)} (DLC)no2020114212",  # noqa
    }
    assert expected == replacements[-1]


def test_replacement_converter_missing_label(deprecated_internal_entries):
    deprecated = deprecated_internal_entries[:1]

    converter = LCSHReplacementConverter(
        deprecated,
        [
            [
                # This is purposefully not the corresponding labelling entry
                # for deprecated
                {
                    "id": "https://id.loc.gov/authorities/subjects/sh85143203",
                    "scheme": "LCSH",
                    "subject": "Video games--Law and legislation",
                }
            ]
        ],
    )
    replacements, ids_missing_labels = converter.iter_replacements()
    replacements_list = list(replacements)
    ids_missing_labels_list = list(ids_missing_labels)

    replacements_expected = [
        {
            "time": "2023-01-23T12:01:15",
            "id_src": "https://id.loc.gov/authorities/subjects/sh2008007279",
            "scheme_src": "LCSH",
            "subject_src": deprecated[0]["label"],
            "id_dst": "https://id.loc.gov/authorities/subjects/sh2006005259",
            "scheme_dst": "LCSH",
            "subject_dst": "",  # left unfilled
            "notes": deprecated[0]["deprecated"]["note"],
        }
    ]
    assert replacements_expected == replacements_list
    id_missing_label_expected = (
        "http://id.loc.gov/authorities/subjects/sh2006005259"
    )
    assert [id_missing_label_expected] == ids_missing_labels_list
