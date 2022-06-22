# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH subjects writer."""

import json


class LCSHWriter:
    """Write the vocabulary out."""

    def __init__(self, iterable):
        """Constructor.

        :param iterable: iterable of {id, scheme, subject}
        """
        self.iterable = iterable

    def jsonl(self, filepath):
        """Write out to jsonl.

        Reading from .jsonl is ~149x faster than reading from pyyaml.load.
        """
        with open(filepath, 'w') as f:
            for e in self.iterable:
                json.dump(e, f)
                f.write("\n")
