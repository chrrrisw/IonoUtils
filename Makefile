# help:
# help: IonoUtils Makefile help
# help:

# help: help          - display this makefile's help information
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: docs          - make the html documentation
docs:
	@cd docs/source && sphinx-apidoc --separate --module-first --force --output-dir=api ../../ionoutils
	@cd docs; make html

# help: docs.clean    - make the html documentation
docs.clean:
	@rm -rf docs/build
	@rm -f docs/source/api/*.rst

# help:

.PHONY: help docs