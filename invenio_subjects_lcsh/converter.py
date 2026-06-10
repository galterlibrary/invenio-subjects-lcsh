# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Generic conversion functionality."""

from .mads_rdf_jsonld import (
    main_node_get_subject,
    main_node_is_authorized_heading,
    main_node_is_deprecated,
    node_get_id,
    topic_find_main_node,
)
from .scheme import LCSHScheme


class LCSHRDMConverter:
    """Convert LCSH term into RDM subjects dict."""

    def __init__(self, topics):
        """Constructor.

        :param topics: LCSH Topics iterable
        :type topics: iterable[dict]
        """
        self.topics = topics
        self.lcsh = LCSHScheme()

    def extract_entry(self, topic):
        """Extract relevant dict from LCSH mads-rdf json-ld dict."""
        node_main = topic_find_main_node(topic)

        # Filter out criteria
        if (
            # empty/not found
            not node_main
            or main_node_is_deprecated(node_main)
            or not main_node_is_authorized_heading(node_main)
        ):
            return {}

        subject = main_node_get_subject(node_main)
        if not subject:
            return {}

        entry = {
            "id": node_get_id(node_main),
            "scheme": self.lcsh.name,
            "subject": subject,
        }
        return entry

    def convert(self):
        """Iterator over converted entries."""
        entries_extracted = (
            self.extract_entry(topic) for topic in self.topics
        )
        # filters out all falsey values
        entries_filtered = filter(None, entries_extracted)
        yield from entries_filtered
