# invenio-subjects-lcsh

*LCSH subject terms for InvenioRDM*

<a href="https://pypi.org/project/invenio-subjects-lcsh/">
  <img src="https://img.shields.io/pypi/v/invenio-subjects-lcsh.svg">
</a>

Install this extension to get [Library of Congress Subject Headings](https://id.loc.gov/authorities/subjects.html) into your instance.

Note that this list excludes `-781` geographical variations as it's not their original intent to be independent tagging terms.

## Installation

From your instance directory:

```bash
pipenv install invenio-subjects-lcsh
```

This will add it to your Pipfile.

## Versions
**From 2025.6.4.1 onwards**

This package follows the following format for versions: `YYYY.mm.dd.patch` where

- `YYYY.mm.dd` is the date of retrieval of the LCSH terms with `mm` and `dd` NOT being 0-prefixed.
- `patch` is the patch number (0-indexed) so that multiple releases can be done on the same day (bug/security fixes)

This follows [calendar versioning](https://calver.org/) (for year, month, and day) and adds a patch number at the end. The package is typically updated on a quarterly basis. The following are illustrative (fictitious) examples of how to understand the versioning of this distribution package:

| Last LCSH update included | patch number | version of this project |
| ------------------------- | ------------ | ----------------------- |
| 2025-06-31                | 2            | 2025.6.31.2             |
| 2025-12-01                | 0            | 2025.12.1.0             |

**Prior to 2025.6.4.1**

This repository follows [calendar versioning](https://calver.org/) for year and month. It does a "best effort" attempt at tracking the LCSH updates in an *up-to-and-including* version date manner. The following are illustrative cases of how to understand the versioning of this distribution package:

| Last LCSH update included | version of this project | date of release of this project |
| ------------------------- | ----------------------- | ------------------------------- |
| 2024-01-31                | 2024.1.X                | any time after 2024-01-31       |
| 2023-12-31                | 2023.12.X               | any time after 2023-12-31       |


`2021.06.18` is both a valid semantic version and an indicator of the year-month corresponding to the loaded terms.
`18` here is a patch number (not a day).


## Usage

There are 2 types of users for this package. Maintainers of the package and instance operators.

### Update terms in an instance

For instance operators, after you have installed the extension as per the steps above, you will want to reload your instance's fixtures: `pipenv run invenio rdm-records fixtures`. This will install the new terms in your instance.

Alternatively, or if you want to update your already loaded subjects to a new listing (e.g. from one year's list to another), you can update your instance's LCSH subjects as per below. Updating subjects this way takes care of everything for you: the subjects themselves and the records/drafts using those subjects. **WARNING** This operation can _remove_ subjects.

```bash
# In your instance's project
# Download up-to-date listings
invenio galter_subjects lcsh download -d /path/to/downloads/storage/
# Generate deprecated entries - metadata expert COULD look at them
invenio galter_subjects lcsh deprecated /path/to/downloads/storage/subjects.skosrdf.jsonld --output-file /path/to/deprecated.csv
# Generate replacement entries from those - metadata expert COULD look at them
invenio galter_subjects lcsh replacements /path/to/deprecated.csv --output-file /path/to/replacements.csv
# Generate file containing deltas to transition your instance to the downloaded listing - metadata expert SHOULD look at them
invenio galter_subjects lcsh deltas --subjects-file /path/to/downloads/storage/subjects.skosrdf.jsonld --replacements-file /path/to/replacements.csv -o /path/to/deltas_lcsh.csv
# Update your instance - *this operation will modify your instance*
invenio galter_subjects update /path/to/deltas_lcsh.csv
```

Look at the help text for these commands to see additional options that can be passed.
In particular, options for `galter_subjects update` allow you to store renamed, replaced or removed subjects on records according to a template of your choice.

### Maintain the initial vocabulary list

When a new list of LCSH terms comes out, this package should be updated to provide an up-to-date starting fixture. Here we show how.

**Pre-requisite/Context**

[Install the distribution package for development](#development) before you do anything.

**Commands**

Once you have that dependency installed, you can run the following commands (`(venv)` denotes the isolated environment):

```bash
# In this project
# Download up-to-date listings
(venv) invenio galter_subjects lcsh download -d /path/to/downloads/storage/
# Generate file containing initial listing
(venv) invenio galter_subjects lcsh file -d /path/to/downloads/storage/ -o invenio_subjects_lcsh/vocabularies/subjects_lcsh.csv
```

When you are happy with the list, bump the version in `pyproject.toml` and release it.

## Development

Install the project in editable mode with `dev` dependencies in an isolated virtualenv (`(venv)` denotes that going forward):

```bash
(venv) pip install -e .[dev]
# or if using pipenv
pipenv run pip install -e .[dev]
# or if using uv
uv venv
uv pip install -e .[dev]
```

Run tests:

```bash
(venv) invoke test
# or shorter
(venv) inv test
# or if using pipenv
pipenv run inv test
# or if using uv
uv run inv test
```

Check manifest:

```bash
(venv) inv check-manifest
# or if using pipenv
pipenv run inv check-manifest
# or if using uv
uv run inv check-manifest
```

Clean out artefacts:

```bash
(venv) inv clean
# or if using pipenv
pipenv run inv clean
# or if using uv
uv run inv clean
```
