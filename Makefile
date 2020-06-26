#!/usr/bin/make

.DEFAULT_GOAL := adjustkeys

PY_SRCS = $(wildcard *.py)

adjustkeys: $(PY_SRCS)
	zip $@.zip $^
	echo '#!/usr/bin/python3' | cat - $@.zip > $@
	chmod 700 $@

clean:
	$(RM) -r __pycache__/ adjustkeys adjustkeys.zip
.PHONY: clean

run: adjustkeys
	python3 $<
.PHONY: run
