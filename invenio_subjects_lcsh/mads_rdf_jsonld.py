# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""MADS RDF JSON-LD manipulation specific code.

The code below uses a functional style relying on lazy iterators because a
large amount of data has to be parsed (1.5GB) and we want to keep the memory
footprint low and the operation speed high.
"""

import sys
from datetime import datetime
from functools import reduce
from itertools import takewhile


def node_get_id(node):
    """Get id with http -> https.

    :param node: dict - mads rdf node of any kind
    :return: string - topic/heading id
    """
    return node.get("@id", "").replace("http://", "https://")


def node_get_list(node, key):
    """Ensure a list is retrieved for `key` in `node`.

    In MADS RDF, a value that is usually a list of dicts, can be a single dict
    when there is only a single value. This function papers over this
    difference to always return a list.

    :param node: dict - mads rdf node of any kind
    :param key: str - key where value can be a list[dict] or a dict
    :return: list[dict] - original list[dict] or dict wrapped in list
    """
    value = node.get(key, [])

    if isinstance(value, dict):
        return [value]
    elif isinstance(value, list):
        return value
    else:
        print(
            f"{node} is neither a dict nor a list - skipped",
            file=sys.stderr,
        )
        return []


def main_node_is_deprecated(node_main):
    """Filter for deprecated topic/heading.

    :param node_main: dict. main @graph node
    :return: bool. deprecated topic/heading or not
    """
    return "madsrdf:DeprecatedAuthority" in node_main.get("@type", [])


def main_node_is_authorized_heading(node_main):
    """Filter for authorized (top-level) topic/heading.

    :param node_main: dict. main @graph node
    :return: bool. authorized topic/heading or not
    """
    mads_collections_member_of = node_get_list(
        node_main, "madsrdf:isMemberOfMADSCollection"
    )
    collection_for_authorized_headings = "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings"  # noqa
    return any(
        c.get("@id") == collection_for_authorized_headings
        for c in mads_collections_member_of
    )


def main_node_get_subject(node_main):
    """Get subject label.

    :param node_main: dict - main @graph node
    :return: string - topic/heading label ("subject" in RDM parlance)
    """
    node_label = (
        node_main.get("madsrdf:authoritativeLabel", {}) or
        # usually for deprecated entries
        node_main.get("madsrdf:variantLabel", {})
    )
    subject = node_label.get("@value")
    return subject


def main_node_get_replacement_ids(node_main):
    """Get replacment ids.

    :param node_main: dict - main @graph node
    :return: list<string> - list of ids to use instead (may be empty or single)
    """
    # can be a dict when a single value is recommended
    use_instead = node_get_list(node_main, "madsrdf:useInstead")
    ids = [node_get_id(n) for n in use_instead]
    ids_replacement = filter(None, ids)
    return list(ids_replacement)


def topic_find_main_node(topic):
    """Find main topic node among topic's graph.

    :param topic: dict. raw skos/mads-rdf topic
    """
    id_suffix = topic["@id"]
    node_main = next(
        (n for n in topic["@graph"] if n.get("@id", "").endswith(id_suffix)),
        {},
    )
    return node_main


def topic_find_deprecation_node(topic):
    """Find deprecation node among topic's graph.

    :param topic: mads rdf json dict - LCSH Topic
    :returns: dict - deprecation node
    """
    node_deprecated = next(
        (
            node
            for node in topic["@graph"]
            if node.get("ri:recordStatus") == "deprecated"
        ),
        {},
    )
    return node_deprecated


def topic_deprecated_since(topic, since=None):
    """Filter for topic having happened from `since` (inclusive) to present.

    :param topic: dict - LCSH mads rdf jsonld topic/heading
    :param since: datetime.datetime - date since to filter by (included)
    """
    if not since:
        return True

    node_deprecation = topic_find_deprecation_node(topic)
    date_created_str = (
        node_deprecation
        .get("ri:recordChangeDate", {})
        .get("@value", "0-01-01T00:00:00")
    )
    date_created = datetime.strptime(date_created_str, "%Y-%m-%dT%H:%M:%S")
    return since <= date_created


def topic_is_deprecated(topic):
    """Check if topic is deprecated heading.

    :param topic: mads rdf json dict - LCSH Topic
    :returns: bool - deprecated or not
    """
    node_main = topic_find_main_node(topic)
    return main_node_is_deprecated(node_main)


def topic_to_replacement(topic):
    """Generate replacement dict.

    May have multiple new ids and no new subjects. This information is
    enhanced in a second pass and selected by curator.

    :param topic: mads rdf json dict - LCSH Topic
    :type topic: dict
    :yields: replacement dict of the shape:
        {
            "id": ...,
            "subject": ...,
            "time": ...,
            "new_id": ...,
            "new_subject": ...,
            "notes": ...
        }
    """
    node_main = topic_find_main_node(topic)
    node_deprecation = topic_find_deprecation_node(topic)
    ids_replacement = main_node_get_replacement_ids(node_main)
    return {
        "time": node_deprecation.get("ri:recordChangeDate", {}).get("@value"),
        "id": node_get_id(node_main),
        "subject": main_node_get_subject(node_main),
        "new_id": "\n".join(ids_replacement),
        "new_subject": "",  # don't bother in this pass, enhanced later
        "notes": node_main.get("madsrdf:deletionNote", {}).get("@value"),
    }


def topics_to_replacements(topics, since=None):
    """Iteratively filter+convert LCSH terms into internal replacement dicts.

    Selects topics that are deprecated and converts them into replacement
    dicts.

    :param topics: iterable of mads rdf json dict - LCSH Topics
    :param since: datetime.datetime - date (included) and later to select for
    :yields: iterable of replacement dicts of the shape:
        {
            "time": ...,
            "id": ...,
            "subject": ...,
            "new_id": ...,
            "new_subject": ...,
            "notes": ...
        }
    """

    def _topic_is_selected(topic):
        """Criteria for being selected (is a replaced entry)."""
        return (
            topic_is_deprecated(topic) and
            topic_deprecated_since(topic, since)
        )

    topics_selected = filter(_topic_is_selected, topics)
    replacements = (topic_to_replacement(topic) for topic in topics_selected)
    yield from replacements


def enhance_replacements_w_new_subjects(replacements, topics):
    """Fill out the new_subject section of passed replacements.

    Idea is that we:
    1) iterate through replacements to establish the ids that need a subject
       (label)
    2) iterate through topics to fill those subjects
    3) iterate through replacements again to fill new_subject w/ those subjects

    :param replacements: iterable of replacement dicts
    :param topics: iterable of mads rdf json dict - LCSH Topics
    :return: iterable of replacement dicts with new_subject filled
    """
    # 1) Initialize ids_dict
    def _gather_ids(ids_dict, replacement):
        # will have None values
        ids_current_dict = dict.fromkeys(replacement["new_id"].split("\n"))
        ids_dict.update(ids_current_dict)
        return ids_dict

    # Assumes replacements is small enough to be consumed into memory
    # completely
    replacements_list = list(replacements)
    # gather all ids for which we want a subject (label)
    # reasonable to list in memory as it should be much smaller than topics
    ids_dict = reduce(_gather_ids, replacements_list, {})

    # 2) Fill ids_dict
    def _ids_dict_has_none_values(topic):
        """Predicate to stop iteration if no more None values.

        Doesn't care about topic.
        """
        return not all(ids_dict.values())

    def _assign_subject(ids_dict, topic):
        node_main = topic_find_main_node(topic)
        id_ = node_get_id(node_main)

        if id_ not in ids_dict:
            return  # continue iteration

        ids_dict[id_] = main_node_get_subject(node_main)

    [
        _assign_subject(ids_dict, topic) for topic in
        takewhile(_ids_dict_has_none_values, topics)
    ]

    # 3) Fill replacements
    def _enhance_replacement_w_subject(r, ids_dict):
        subjects = [
            # fallback to empty string in case no labels were found (!)
            ids_dict.get(new_id, "") or "" for new_id in
            r["new_id"].split("\n")
        ]
        r["new_subject"] = "\n".join(subjects)
        return r

    return (
        _enhance_replacement_w_subject(r, ids_dict) for r in replacements_list
    )
