#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_CAPS_SRCS = $(shell ./deps adjustcaps.py)
ADJUST_GLYPHS_SRCS = $(shell ./deps adjustglyphs.py)
DIST_CONTENT = adjustcaps adjustglyphs $(wildcard profiles/kat/*.obj profiles/kat/*.yml) $(wildcard examples/*) layout_row_profiles.yml layout.yml README.md

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
	# mv bin_$@/$(@).py bin_$@/__main__.py
	echo -e 'if __name__ == "__main__":\n    with open("$@", "r") as f:\n        exec(f.read())' > bin_$@/__main__.py
	cd bin_$@/ && zip $@.zip $(shell echo $^ | tr ' ' '\n') __main__.py >/dev/null && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$@/$@.zip > $@
	chmod 700 $@
endef

dist: $(DIST_CONTENT)
	zip -o adjust-keys.zip $^

adjustglyphs: $(ADJUST_GLYPHS_SRCS)
	$(compilePython)

adjustcaps: $(ADJUST_CAPS_SRCS)
	$(compilePython)

profiles/kat/%.yml %.yml:
	@# Do nothing
profiles/kat/%.obj:
	@# Do nothing
examples/%:
	@# Do nothing
%.md:
	@# Do nothing

clean:
	$(RM) -r __pycache__/ adjustglyphs bin_adjustglyphs adjustglyphs.zip adjustcaps bin_adjustcaps adjustcaps.zip *.c
.PHONY: clean
