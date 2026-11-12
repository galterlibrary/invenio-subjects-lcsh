#
# Copyright (C) 2024-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Generic conversion functionality."""

from itertools import chain, takewhile

from .scheme import LCSHScheme, identify_scheme


def to_rdm_id(id_of_subject):
    """Convert LCSH id to RDM LCSH id."""
    return id_of_subject.replace("http://", "https://")


def to_internal_entry_id(id_of_subject):
    """Convert RDM LCSH id to LCSH id."""
    return id_of_subject.replace("https://", "http://")


class LCSHRDMConverter:
    """Convert LCSH term into RDM subjects dict."""

    def __init__(self, internal_entries):
        """Constructor.

        Args:
            internal_entries (dict - internal entry shape): internal LCSH entry
        """
        self.internal_entries = internal_entries
        self.lcsh = LCSHScheme()

    def convert_entry(self, entry):
        """Extract relevant dict from LCSH mads-rdf json-ld dict."""
        return {
            "id": to_rdm_id(entry["id"]),
            "scheme": self.lcsh.name,
            "subject": entry["label"],
        }

    def iter_rdm_subjects(self):
        """Iterator over converted entries."""
        yield from (
            self.convert_entry(entry) for entry in self.internal_entries
        )


class LCSHReplacementConverter:
    """Convert internal entries into replacement entries."""

    def __init__(self, entries_deprecated, labelling_sources):
        """Constructor.

        Args:
            entries_deprecated (dict - internal entry shape): internal LCSH
                                                              entry
            labelling_sources (iterable[dict - internal entry shape]):
                iterable internal LCSH entries for labelling purposes
        """
        self._entries_deprecated = entries_deprecated
        self.lcsh = LCSHScheme()
        self._subjects_rdm = chain.from_iterable(labelling_sources)

    def _to_unlabelled_replacement_entry(self, entry):
        """Convert entry.

        Args:
            entry (dict - internal entry shape): read LCSH

        Returns:
            dict - replacement shape: replacement dict
        """
        return {
            "time": entry["deprecated"]["time"],
            "id_src": to_rdm_id(entry["id"]),
            "scheme_src": self.lcsh.name,
            "subject_src": entry["label"],
            "id_dst": "\n".join(
                [to_rdm_id(rid) for rid in entry["deprecated"]["replacements"]]
            ),
            "scheme_dst": "\n".join(
                [
                    identify_scheme(to_rdm_id(rid))
                    for rid in entry["deprecated"]["replacements"]
                ]
            ),
            "subject_dst": "",  # don't bother in this pass, enhanced later
            "notes": entry["deprecated"]["note"],
        }

    def _assign_subject(self, subject, id_to_label_mapping):
        """Assign fill mapping with subject information.

        Args:
            subject (dict - RDM subject shape): subject with all information
            id_to_label_mapping (dict[string, string]): id to label mapping
        """
        id_of_subject = subject["id"]

        if id_of_subject not in id_to_label_mapping:
            return  # do nothing

        id_to_label_mapping[id_of_subject] = subject["subject"]

    def _get_id_to_label_mapping(self, replacements_unlabelled_list):
        # 1) Get ids of all recommended replacements
        iterable_of_list_of_replacement_ids = (
            replacement["id_dst"].splitlines()
            for replacement in replacements_unlabelled_list
        )
        # flatten out iter[list[replacement_id]] to iter[replacement_id]
        replacement_ids = chain.from_iterable(
            iterable_of_list_of_replacement_ids
        )
        replacement_id_to_label = {rid: "" for rid in replacement_ids}

        # 2) Fill id_to_label
        [
            self._assign_subject(subject, replacement_id_to_label)
            for subject in takewhile(
                # while not all ids have a label
                lambda e: not all(replacement_id_to_label.values()),
                self._subjects_rdm,
            )
        ]

        return replacement_id_to_label

    def _label_subject_dst(self, replacement_entry, id_to_label):
        """Fill in the new subject field.

        Args:
            replacement_entry (_type_): _description_
            id_to_label (_type_): _description_

        Returns:
            replacement_entry (dict - replacement entry shape): with subject

        """
        subjects = [
            # fallback to empty string in case no labels were found
            id_to_label.get(id_, "")
            for id_ in replacement_entry["id_dst"].splitlines()
        ]
        replacement_entry["subject_dst"] = "\n".join(subjects)
        return replacement_entry

    def iter_replacements(self):
        """Iterator over replacemnt entries.

        Replacement dict has this shape:
            {
                "time": ...,
                "id_src": ...,
                "scheme_src": ...,
                "subject_src": ...,
                "id_dst": ...,
                "scheme_dst": ...,
                "subject_dst": ...,
                "notes": ...
            }

        Yields:
            dict - replacement entry shape: replacement dict
        """
        # Keep as a list to iterate over multiple times
        unlabelled_replacements_list = [
            self._to_unlabelled_replacement_entry(e)
            for e in self._entries_deprecated
        ]

        id_to_label = self._get_id_to_label_mapping(
            unlabelled_replacements_list
        )

        return (
            (
                self._label_subject_dst(r, id_to_label)
                for r in unlabelled_replacements_list
            ),
            # ones that have no label
            (
                to_internal_entry_id(id_)
                for id_ in id_to_label if not id_to_label[id_]
            ),
        )
