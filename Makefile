
.PHONY: install update test

install:
	pipenv run pip install -e .[all]

update:
	@ echo "TODO!"
	# pipenv run invenio-subjects-lcsh

test:
	pipenv run ./run-tests.sh
