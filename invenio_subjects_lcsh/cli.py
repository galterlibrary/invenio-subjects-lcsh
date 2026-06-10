# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH Command line tool."""

from datetime import datetime
from functools import partial, wraps
from pathlib import Path

import click
from flask.cli import with_appcontext
from galter_subjects_utils.adapter import converted_to_subjects
from galter_subjects_utils.deltor import DeltasGenerator
from galter_subjects_utils.keeptrace import KeepTrace
from galter_subjects_utils.reader import get_rdm_subjects, read_csv, read_jsonl
from galter_subjects_utils.writer import write_csv

from .adapter import generate_replacements
from .converter import LCSHRDMConverter
from .downloader import LCSHDownloader
from .mads_rdf_jsonld import (
    enhance_replacements_w_new_subjects,
    topics_to_replacements,
)
from .scheme import LCSHScheme

defaults = {
    "downloads-dir": Path.cwd(),
    "output-file": Path.cwd(),
}


option_lcsh_downloads_dir = partial(
    click.option(
        "--downloads-dir",
        "-d",
        type=click.Path(path_type=Path),
        default=defaults["downloads-dir"],
    )
)


def lcsh_download_options(f):
    """Encapsulate common LCSH download options."""

    @option_lcsh_downloads_dir
    @click.option(
        "--no-cache",
        default=False,
        help="Re-download even if already downloaded.",
        is_flag=True,
    )
    @wraps(f)
    def _wrapped(*args, **kwargs):
        """Wrap f with common download options."""
        return f(*args, **kwargs)

    return _wrapped


def to_lcsh_downloader_kwargs(parameters):
    """To LCSHDownloader kwargs."""
    result = {
        "cache": not parameters["no_cache"],
        "directory": Path.cwd() / parameters["downloads_dir"],
    }
    return result


@click.group()
def lcsh():
    """LCSH related commands."""


@lcsh.command("download")
@lcsh_download_options
def lcsh_download(**parameters):
    """Download LCSH files."""
    downloader_kwargs = to_lcsh_downloader_kwargs(parameters)
    downloader = LCSHDownloader(**downloader_kwargs)
    downloader.download()

    print(f"Raw LCSH files written in {parameters['downloads_dir']}/")


def to_lcsh_converter_kwargs(downloader):
    """Provide LCSH converter args from `downloader`."""
    return {"topics": read_jsonl(downloader.terms_filepath)}


@lcsh.command("file")
@lcsh_download_options
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default=defaults["output-file"] / "subjects_lcsh.csv",
)
def lcsh_file(**parameters):
    """Generate new LCSH subjects file."""
    downloader_kwargs = to_lcsh_downloader_kwargs(parameters)
    downloader = LCSHDownloader(**downloader_kwargs)

    # Convert
    converter_kwargs = to_lcsh_converter_kwargs(downloader)
    converter = LCSHRDMConverter(**converter_kwargs)
    converted = converter.convert()
    # Exclude special automated geographic terms
    converted_filtered = (s for s in converted if not s["id"].endswith("-781"))

    # Write
    header = ["id", "scheme", "subject"]
    filepath = write_csv(
        converted_filtered,
        parameters["output_file"],
        writer_kwargs={"fieldnames": header},
    )

    print(f"LCSH terms written here {filepath}")


@lcsh.command("replacements")
@click.argument(
    "subjects-file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--since", "-s", default=None, help="Filter for YYYY-MM-DD and later."
)
@click.option(
    "--output-file", "-o", type=click.Path(path_type=Path),
    default=Path.cwd() / "replacements_lcsh.csv"
)
def lcsh_replacements(**parameters):
    """Generate (initial) CSV file of deprecated+replacement LCSH topics.

    This file is then parsed by a metadata expert and potentially edited
    for subsequent use in lcsh_deltas. In particular, metadata experts
    should select the id + subject (if any) to replace a deprecated heading
    that has no or multiple replacement options for each such heading.
    """
    fp_of_subjects = parameters["subjects_file"].expanduser()

    since = parameters["since"]
    since = datetime.strptime(since, "%Y-%m-%d") if since else None

    topics_raw = read_jsonl(fp_of_subjects)
    # deprecated dicts with replacement id only
    replacements = topics_to_replacements(topics_raw, since)
    # fill out corresponding subject if possible
    # need to read topics again
    topics_raw = read_jsonl(fp_of_subjects)
    replacements = enhance_replacements_w_new_subjects(replacements, topics_raw)  # noqa

    header = ["time", "id", "subject", "new_id", "new_subject", "notes"]

    write_csv(
        replacements,
        parameters["output_file"],
        writer_kwargs={"fieldnames": header},
    )

    print(f"LCSH replacements written here {parameters['output_file']}")


@lcsh.command("deltas")
@click.option(
    "--subjects-file",
    "-s",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
)
@click.option(
    "--replacements-file",
    "-r",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default=defaults["output-file"] / "deltas.csv",
)
@with_appcontext
def lcsh_deltas(**parameters):
    """Write LCSH subject delta operations to file."""
    print("Generating deltas...")
    lcsh = LCSHScheme()

    # Source subjects
    subjects_rdm_preexisting = get_rdm_subjects(scheme=lcsh.name)
    src = converted_to_subjects(
        subjects_rdm_preexisting,
        prefix=lcsh.prefix,
    )

    # Destination subjects
    fp_of_subjects = parameters["subjects_file"]
    topics_raw = read_jsonl(fp_of_subjects)
    converted = LCSHRDMConverter(topics_raw).convert()
    # Exclude special automated geographic terms
    converted_filtered = (s for s in converted if not s["id"].endswith("-781"))
    dst = converted_to_subjects(converted_filtered, prefix=lcsh.prefix)

    # Replacements
    fp_of_replacements = parameters["replacements_file"]
    replacements_lcsh = read_csv(fp_of_replacements)
    replacements = generate_replacements(replacements_lcsh)

    ops = DeltasGenerator(
        src_subjects=src,
        dst_subjects=dst,
        scheme=lcsh,
        replacements=replacements,
    ).generate()
    # in-place
    KeepTrace.mark(
        ops,
        # only can keep trace of *those* anyway
        yes_logic=lambda op: op["type"] in ["rename", "replace", "remove"],
    )

    fp_of_deltas = parameters["output_file"]
    header = [
        "id",
        "type",
        "scheme",
        "subject",
        "new_id",
        "new_subject",
        "keep_trace",
    ]
    write_csv(ops, fp_of_deltas, writer_kwargs={"fieldnames": header})

    print(f"LCSH deltas written here {fp_of_deltas}")
