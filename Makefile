init:
	pip3 install -r requirements.txt

test:
	/usr/bin/env python3 -m pytest --cov-config tests/coverage.rc --cov=dyna --cov-report=term --cov-report=annotate:cov_annotate tests

.PHONY: init test

