#
# Copyright (C) 2024-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH Scheme."""

from galter_subjects_utils.scheme import Scheme


class LCSHScheme(Scheme):
    """LCSH scheme."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            name="LCSH",
            prefix="https://id.loc.gov/authorities/subjects/"
        )

class LCNAFScheme(Scheme):
    """LCNAF scheme."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            name="LCNAF",
            prefix="https://id.loc.gov/authorities/names/",
        )


KNOWN_SCHEMES = [
    LCSHScheme(),
    LCNAFScheme(),
]


def identify_scheme(id_of_rdm_entry):
    """Identify scheme name of given internal entry id.

    Args:
        id_of_rdm_entry (str): internal entry id

    Returns:
        str: Scheme name of id
    """
    for scheme in KNOWN_SCHEMES:
        if id_of_rdm_entry.startswith(scheme.prefix):
            return scheme.name
    return ""
