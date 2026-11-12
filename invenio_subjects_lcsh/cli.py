#
# Copyright (C) 2026 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH Command line tool."""

from datetime import datetime
from pathlib import Path

import click
from flask.cli import with_appcontext
from galter_subjects_utils.adapter import converted_to_subjects
from galter_subjects_utils.deltor import DeltasGenerator
from galter_subjects_utils.keeptrace import KeepTrace
from galter_subjects_utils.reader import get_rdm_subjects, read_csv
from galter_subjects_utils.writer import write_csv

from .adapter import generate_replacements
from .converters import LCSHRDMConverter, LCSHReplacementConverter
from .downloader import LCSHDownloader
from .filters import (
    deprecated_since_filter,
    non_geographic_filter,
    valid_heading_filter,
)
from .readers import LCSHMadsRdfJsonLdReader
from .scheme import LCSHScheme

defaults = {
    "downloads-dir": Path.cwd(),
    "output-file": Path.cwd(),
}


option_lcsh_downloads_dir = click.option(
    "--downloads-dir",
    "-d",
    type=click.Path(path_type=Path),
    default=defaults["downloads-dir"],
)


@click.group()
def lcsh():
    """LCSH related commands."""


@lcsh.command("download")
@option_lcsh_downloads_dir
@click.option(
    "--no-cache",
    default=False,
    help="Re-download even if already downloaded.",
    is_flag=True,
)
def lcsh_download(**parameters):
    """Download LCSH files."""
    downloader = LCSHDownloader(
        cache=not parameters["no_cache"],
        directory=Path.cwd() / parameters["downloads_dir"],
    )
    downloader.download()

    print(f"Raw LCSH files written in {parameters['downloads_dir']}/")


@lcsh.command("file")
@option_lcsh_downloads_dir
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default=defaults["output-file"] / "subjects_lcsh.csv",
)
def lcsh_file(**parameters):
    """Generate new LCSH subjects file."""
    # 'Empty' downloader just to pass it to reader, so that it can retrieve
    # relevant filepaths.
    downloader = LCSHDownloader(directory=parameters["downloads_dir"])

    # Read
    reader = LCSHMadsRdfJsonLdReader(
        downloader.terms_filepath,
        filter=valid_heading_filter,
    )

    # Convert
    converter = LCSHRDMConverter(reader.iter_internal_entries())

    # Write
    header = ["id", "scheme", "subject"]
    filepath = write_csv(
        converter.iter_rdm_subjects(),
        parameters["output_file"],
        writer_kwargs={"fieldnames": header},
    )

    print(f"LCSH terms written here {filepath}")


@lcsh.command("replacements")
@option_lcsh_downloads_dir
@click.option(
    "--lcsh",
    type=click.Path(path_type=Path),
    default=Path(__file__).parent / "vocabularies/subjects_lcsh.csv",
)
@click.option(
    "--lcnaf",
    type=click.Path(path_type=Path),
)
@click.option(
    "--since",
    "-s",
    default=None,
    help="Filter for YYYY-MM-DD and later.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "replacements_lcsh.csv",
)
def lcsh_replacements(**parameters):
    """Generate CSV file of deprecated w/ replacement LCSH topics.

    This file is typically used directly to generate deltas, so that
    only deltas are reviewed by a metadata curator.
    """
    downloader = LCSHDownloader(directory=parameters["downloads_dir"])

    since = parameters["since"]
    since = datetime.strptime(since, "%Y-%m-%d") if since else None

    # Read deprecated
    reader_deprecated = LCSHMadsRdfJsonLdReader(
        downloader.terms_filepath,
        filter=lambda e: (
            # Deprecated entries have no collections so
            # authorized_heading_filter cannot be used.
            # If any non authorized but deprecated headings are picked up
            # they will simply lead to no-ops. In practice, those have not
            # been encountered in recent runs.
            non_geographic_filter(e) and
            deprecated_since_filter(e, since)
        )
    )

    # Sources to use to find labels of ids recommended to replace deprecated
    # ones
    sources_for_new_subject_labels = [
        read_csv(parameters["lcsh"]),
    ]
    if parameters.get("lcnaf"):
        sources_for_new_subject_labels.append(read_csv(parameters["lcnaf"]))

    converter = LCSHReplacementConverter(
        reader_deprecated.iter_internal_entries(),
        sources_for_new_subject_labels
    )
    replacements, ids_missing_label = converter.iter_replacements()

    header = [
        "time",
        "id_src",
        "scheme_src",
        "subject_src",
        "id_dst",
        "scheme_dst",
        "subject_dst",
        "notes",
    ]
    write_csv(
        replacements,
        parameters["output_file"],
        writer_kwargs={"fieldnames": header},
    )
    fp_of_ids_missing_label = (
        parameters["output_file"].parent / "ids_missing_label.csv"
    )
    write_csv(
        ({"id": id_} for id_ in ids_missing_label),
        fp_of_ids_missing_label,
        writer_kwargs={"fieldnames": ["id"]},
    )

    print(f"LCSH replacements written here {parameters['output_file']}")
    print(f"ids with missing label written here {fp_of_ids_missing_label}")


@lcsh.command("deltas")
@click.option(
    "--lcsh",
    type=click.Path(path_type=Path),
    default=Path(__file__).parent / "vocabularies/subjects_lcsh.csv",
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
    # The generated file actually
    subjects_rdm = read_csv(parameters["lcsh"])
    dst = converted_to_subjects(subjects_rdm, prefix=lcsh.prefix)

    # Replacements
    replacements_lcsh = read_csv(parameters["replacements_file"])
    replacements = generate_replacements(replacements_lcsh)

    deltas_generator = DeltasGenerator(
        src_subjects=src,
        dst_subjects=dst,
        replacements=replacements,
    )
    deltas = list(deltas_generator.iter_deltas())
    # in-place
    KeepTrace.mark(
        deltas,
        # only can keep trace of *those* anyway
        yes_logic=lambda delta: delta["type"] in ["edit", "replace", "remove"],
    )

    fp_of_deltas = parameters["output_file"]
    header = [
        "type",
        "id_src",
        "scheme_src",
        "subject_src",
        "id_dst",
        "scheme_dst",
        "subject_dst",
        "keep_trace",
    ]
    write_csv(
        deltas,
        fp_of_deltas,
        writer_kwargs={"fieldnames": header},
    )

    print(f"LCSH deltas written here {fp_of_deltas}")
