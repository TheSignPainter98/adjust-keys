#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_KEYS_SRCS = $(shell ./deps adjustkeys_main.py)
GLYPH_INF_KEYS_SRCS = $(shell ./deps glyphinf_main.py)

all: adjustkeys glyphinf
.PHONY: all

define compilePython
	$(RM) -r bin/
	cython3 -X language_level=3 $^
	mkdir bin
	cp $^ bin
	mv bin/$(@)_main.py bin/__main__.py
	cd bin/ && zip $@.zip $(shell echo $^ | tr ' ' '\n' |  grep -v $(@)_main) __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin/$@.zip > $@
	chmod 700 $@
endef

adjustkeys: $(ADJUST_KEYS_SRCS)
	$(compilePython)

glyphinf: $(GLYPH_INF_KEYS_SRCS)
	$(compilePython)

clean:
	$(RM) -r __pycache__/ adjustkeys adjustkeys.zip *.c
.PHONY: clean

run: adjustkeys
	python3 $<
.PHONY: run
