#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_KEYS_SRCS = $(shell ./deps adjustkeys_main.py)
GLYPH_INF_KEYS_SRCS = $(shell ./deps glyphinf_main.py)

all: adjustkeys glyphinf
.PHONY: all

adjustkeys: $(ADJUST_KEYS_SRCS)
	$(RM) -r bin/
	mkdir bin
	cp $^ bin
	mv bin/adjustkeys_main.py bin/__main__.py
	cd bin/ && zip $@.zip $(shell echo $^ | tr ' ' '\n' |  grep -v adjustkeys_main) __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin/$@.zip > $@
	chmod 700 $@

glyphinf: $(GLYPH_INF_KEYS_SRCS)
	$(RM) -r bin/
	mkdir bin
	cp $^ bin
	mv bin/glyphinf_main.py bin/__main__.py
	cd bin/ && zip $@.zip $(shell echo $^ | tr ' ' '\n' |  grep -v glyphinf_main) __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin/$@.zip > $@
	chmod 700 $@

clean:
	$(RM) -r __pycache__/ adjustkeys adjustkeys.zip
.PHONY: clean

run: adjustkeys
	python3 $<
.PHONY: run
