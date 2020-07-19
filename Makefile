#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_CAPS_SRCS = $(shell ./deps adjustcaps.py)
ADJUST_GLYPHS_SRCS = $(shell ./deps adjustglyphs.py)

all: adjustglyphs adjustcaps
.PHONY: all

define compilePython
	$(RM) -r bin_$@/
	cython3 -X language_level=3 $^
	mkdir bin_$@
	cp $^ bin_$@
	mv bin_$@/$(@).py bin_$@/__main__.py
	cd bin_$@/ && zip $@.zip $(shell echo $^ | tr ' ' '\n' |  grep -v $(@).py) __main__.py >/dev/null && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$@/$@.zip > $@
	chmod 700 $@
endef

adjustglyphs: $(ADJUST_GLYPHS_SRCS)
	$(compilePython)

adjustcaps: $(ADJUST_CAPS_SRCS)
	$(compilePython)

clean:
	$(RM) -r __pycache__/ adjustglyphs bin_adjustglyphs adjustglyphs.zip adjustcaps bin_adjustcaps adjustcaps.zip *.c
.PHONY: clean
