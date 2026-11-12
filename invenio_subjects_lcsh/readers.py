#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Readers for LCSH data dumps.

Readers iterate over the content of the data dump, returning
internal representations of the topic, so that filters or converters have
a common and uniform interface to work with.

"""
from galter_subjects_utils.reader import read_jsonl

from invenio_subjects_lcsh.sources.mads_rdf_jsonld import (
    main_node_get_replacement_ids,
    main_node_get_subject,
    main_node_is_deprecated,
    node_get_list,
    topic_find_deprecation_node,
    topic_find_main_node,
)


class LCSHMadsRdfJsonLdReader:
    """Reader class for LCSH MADS RDF Json-ld file."""

    def __init__(self, filepath, filter=lambda e: True):
        """Constructor."""
        self._filepath = filepath
        self._filter = filter

    def _raw_to_internal_entry(self, raw):
        """Convert raw entry to internal representation entry.

        Args:
            raw (dict - MADS-RDF node): read LCSH

        Returns:
            dict - internal entry shape: internal entry
        """
        node = raw
        node_main = topic_find_main_node(node)
        node_deprecation = topic_find_deprecation_node(node)
        entry = {
            "id": node_main.get("@id", ""),
            "label": main_node_get_subject(node_main),
            "deprecated": {
                "status": main_node_is_deprecated(node_main),
                "note": (
                    node_main.get("madsrdf:deletionNote", {}).get("@value", "")
                ),
                "replacements": main_node_get_replacement_ids(node_main),
                "time": (
                    node_deprecation
                    .get("ri:recordChangeDate", {})
                    .get("@value", "")
                ),
            },
            "collections": [
                c["@id"]
                for c in node_get_list(
                    node_main,
                    "madsrdf:isMemberOfMADSCollection",
                )
                if "@id" in c
            ],
        }
        return entry

    def iter_internal_entries(self):
        """Iteratively read entries from MADS RDF Json-ld file.

        Yields:
            dict - internal entry shape: internal LCSH entry
        """
        entries_raw = read_jsonl(self._filepath)
        entries_internal = (
            self._raw_to_internal_entry(entry) for entry in entries_raw
        )
        entries_filtered = (
            entry for entry in entries_internal
            if entry and self._filter(entry)
        )
        yield from entries_filtered
