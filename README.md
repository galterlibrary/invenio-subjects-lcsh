# invenio-subjects-lcsh

*LCSH subject terms for InvenioRDM*

Install this extension to get [Library of Congress Subject Headings](https://id.loc.gov/authorities/subjects.html) into your instance.

## Installation

From your instance directory:

```bash
pipenv install invenio-subjects-lcsh
```

This will add it to your Pipfile.

## Versions

This repository follows [calendar versioning](https://calver.org/) for year and month:

`2021.06.18` is both a valid semantic version and an indicator of the year-month corresponding to the loaded terms.
`18` here is a patch number (not a day).

So far the package is compatible with InvenioRDM 9.1+'s subjects "ABI". If there is a breaking change, a compatibility
table will be provided to indicate which version is compatible with with InvenioRDM's "ABI".

## Usage

There are 2 types of users for this package. Maintainers of the package and instance administrators.

### Instance administrators

For instance administrators, after you have installed the extension as per the steps above, you will want to reload your instance's fixtures: `pipenv run invenio rdm-records fixtures`. This will install the new terms in your instance.

Updating existing terms currently requires manual replacement.

### Maintainers

This package should probably be updated on a yearly basis. Here we show how.

0. Install this package locally with the `dev` extra:

```bash
pipenv run pip install -e .[dev]
```

1. Use the installed `galter-subjects-utils` tool to get the new list:

```bash
pipenv run galter-subjects-utils lcsh --output-file invenio_subjects_lcsh/vocabularies/subjects_lcsh.jsonl
```

   This will

   1. Download the new list(s)
   2. Read it filtering for topics
   3. Convert terms to InvenioRDM subjects format
   4. Write those to the specified file

2. Check the manifest (it should typically be all good)

```bash
pipenv run inv check-manifest
```

3. When you are happy with the list, bump the version and release it.

## Development

Install the project in editable mode with `dev` dependencies in an isolated virtualenv (`(venv)` denotes that going forward):

```bash
(venv) pip install -e .[dev]
# or if using pipenv
pipenv run pip install -e .[dev]
```

Run tests:

```bash
(venv) invoke test
# or shorter
(venv) inv test
# or if using pipenv
pipenv run inv test
```

Check manifest:

```bash
(venv) inv check-manifest
# or if using pipenv
pipenv run inv check-manifest
```

Clean out artefacts:

```bash
(venv) inv clean
# or if using pipenv
pipenv run inv clean
```
