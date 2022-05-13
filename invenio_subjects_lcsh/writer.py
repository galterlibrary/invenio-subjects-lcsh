# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH subjects writer."""


class LCSHWriter:
    """Write the vocabulary out."""

    def __init__(self, iterable):
        """Constructor.

        :param iterable: iterable of {id, scheme, subject}
        """
        self.iterable = iterable

    def yaml(self, filepath):
        """Write out to yaml.

        We don't rely on the yaml library to write out the values since it
        can't stream-write. Because the values are simple, this is a
        reasonable choice.
        """
        with open(filepath, 'w') as f:
            for e in self.iterable:
                subject = e['subject'].replace('"', r'\"')
                f.write(f"- id: {e['id']}\n")
                f.write(f"  scheme: {e['scheme']}\n")
                f.write(f"  subject: \"{subject}\"\n")
