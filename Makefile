#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_GLYPHS_SRCS = $(shell ./deps adjustglyphs.py)
ADJUST_caps_SRCS = $(shell ./deps adjustcaps_main.py)

all: adjustglyphs adjustcaps
.PHONY: all

define compilePython
	$(RM) -r bin_$@/
	cython3 -X language_level=3 $^
	mkdir bin_$@
	cp $^ bin_$@
	# mv bin_$@/$(@).py bin_$@/__main__.py
	echo -e 'if __name__ == "__main__":\n    with open("$@", "r") as f:\n        exec(f.read())' > bin_$@/__main__.py
	cd bin_$@/ && zip $@.zip $(shell echo $^ | tr ' ' '\n') __main__.py >/dev/null && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$@/$@.zip > $@
	chmod 700 $@
endef

adjustglyphs: $(ADJUST_GLYPHS_SRCS)
	$(compilePython)

adjustcaps: $(ADJUST_caps_SRCS)
	$(compilePython)

clean:
	$(RM) -r __pycache__/ adjustglyphs bin_adjustglyphs adjustglyphs.zip adjustcaps bin_adjustcaps adjustcaps.zip *.c
.PHONY: clean
