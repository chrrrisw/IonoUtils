# help:
# help: IonoUtils Makefile help
# help:

# help: help   - display this makefile's help information
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: doc    - make the html documentation
doc:
	@cd doc/source && sphinx-apidoc --separate --module-first --force --output-dir=api ../..
	@cd doc; make html

# help:

.PHONY: help doc