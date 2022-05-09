# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH term extractor."""

import json


class LCSHExtractor:
    """LCSH extractor."""

    def __init__(self, filepath):
        """Constructor."""
        self.filepath = filepath

    def __iter__(self):
        """Iterate over terms."""
        with open(self.filepath, 'r') as f:
            for line in f.readlines():
                entry = self.extract_entry(line)
                if entry:
                    yield entry

    def extract_entry(self, line):
        """Extract relevant dict from LCSH skos json-ld line."""
        entry = {}
        jsonld_entry = json.loads(line)

        # Find id and label
        id_suffix = jsonld_entry["@id"]
        info_entry = next(
            (
                e for e in jsonld_entry["@graph"]
                if (
                    e.get("@id").endswith(id_suffix) and
                    e.get("@type") == "skos:Concept"
                )
            ),
            None
        )

        if not info_entry:
            return {}

        entry["id"] = info_entry["@id"]
        entry["scheme"] = "LCSH"

        pref_label = info_entry["skos:prefLabel"]
        if isinstance(pref_label, dict):
            subject = pref_label["@value"]
        elif isinstance(pref_label, list):
            subject = pref_label[-1]["@value"]
        else:
            raise Exception("invalid skos:prefLabel")
        entry["subject"] = subject

        return entry
