#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Filters for read LCSH internal entries."""

import datetime as dt


def non_geographic_filter(internal_entry):
    """Filter for non geographic LCSH term.

    Geographic LCSH terms are identified by the -781 identifier suffix.

    Args:
        internal_entry (dict - internal entry shape): read LCSH

    Returns:
        boolean: True if not geographic, False otherwise
    """
    return not internal_entry["id"].endswith("-781")


def deprecated_filter(internal_entry):
    """Filter for deprecated LCSH term.

    Args:
        internal_entry (dict - internal entry shape): read LCSH

    Returns:
        boolean: True if deprecated, False otherwise
    """
    return internal_entry["deprecated"]["status"]


def authorized_heading_filter(internal_entry):
    """Fitler for authorized (top-level, not subdivision) heading.

    Args:
        internal_entry (dict - internal entry shape): read LCSH

    Returns:
        boolean: True if authorized, False otherwise
    """
    collection_for_authorized_headings = "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings"  # noqa
    return any(
        c == collection_for_authorized_headings
        for c in internal_entry["collections"]
    )


def valid_heading_filter(internal_entry):
    """Filter for valid heading.

    Args:
        internal_entry (dict - internal entry shape): read LCSH

    Returns:
        boolean: True if valid, False otherwise
    """
    return (
        non_geographic_filter(internal_entry)
        and not deprecated_filter(internal_entry)
        and authorized_heading_filter(internal_entry)
    )


def deprecated_since_filter(internal_entry, since=None):
    """Filter for deprecated LCSH term since.

    If since is None, this is equivalent to deprecated_filter.

    Args:
        internal_entry (dict - internal entry shape): read LCSH
        since (datetime.datetime, optional): since datetime. Defaults to None.

        boolean: True if deprecated since, False otherwise
    """
    if deprecated_filter(internal_entry):
        time_str = internal_entry["deprecated"]["time"]

        if not since or not time_str:
            return True

        time_dt = dt.datetime.fromisoformat(time_str)
        return since <= time_dt
    else:
        return False
