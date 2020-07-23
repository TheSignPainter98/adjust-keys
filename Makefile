#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_CAPS_SRCS = $(shell ./deps adjustcaps.py)
ADJUST_GLYPHS_SRCS = $(shell ./deps adjustglyphs.py)
DIST_CONTENT = adjustcaps adjustglyphs $(wildcard profiles/kat/*.obj profiles/kat/*.yml) $(wildcard examples/*) README.md LICENSE pkgs.txt adjustcaps.1.gz adjustglyphs.1.gz

all: adjustglyphs adjustcaps
.PHONY: all

ifndef NO_CYTHON
define runCython
	cython3 -X language_level=3 $^
endef
endif

define compilePython
	$(RM) -r bin_$@/
	$(runCython)
	mkdir bin_$@
	cp $^ bin_$@
	cp bin_$@/$(@).py bin_$@/__main__.py
	cd bin_$@/ && zip $@.zip $(shell echo $^ | tr ' ' '\n') __main__.py >/dev/null && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$@/$@.zip > $@
	chmod 700 $@
endef

%.1.gz: %
	(help2man -N --no-discard-stderr ./$< | gzip - -) > $@

dist: $(DIST_CONTENT)
	zip -q -o adjust-keys.zip $^

adjustglyphs: $(ADJUST_GLYPHS_SRCS)
	$(compilePython)

adjustcaps: $(ADJUST_CAPS_SRCS)
	$(compilePython)

pkgs.txt: %.py
	pip freeze > $@

%.py:
	@# Do nothing
profiles/kat/%.yml %.yml:
	@# Do nothing
profiles/kat/%.obj:
	@# Do nothing
examples/%:
	@# Do nothing
%.md:
	@# Do nothing
LICENSE:
	@# Do nothing

clean:
	$(RM) -r __pycache__/ adjustglyphs bin_adjustglyphs adjustglyphs.zip adjustcaps bin_adjustcaps adjustcaps.zip *.c *.zip
.PHONY: clean
