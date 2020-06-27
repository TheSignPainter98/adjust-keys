#!/usr/bin/make

.DEFAULT_GOAL := adjustkeys

ADJUST_KEYS_SRCS = $(shell ./deps adjust_keys_main.py)
GLYPH_INF_KEYS_SRCS = $(shell ./deps adjust_keys_main.py)


adjustkeys: $(ADJUST_KEYS_SRCS)
	$(RM) $(wildcard bin/*)
	mkdir bin
	cp $^ bin
	mv bin/adjust_keys_main.py bin/__main__.py
	zip bin/$@.zip bin/$^
	echo '#!/usr/bin/python3' | cat - bin/$@.zip > $@
	chmod 700 $@

glyphinf: $(GLYPH_INF_KEYS_SRCS)
	$(RM) $(wildcard bin/*)
	mkdir bin
	cp $^ bin
	mv bin/glyphinf_main.py bin/__main__.py
	zip bin/$@.zip bin/$^
	echo '#!/usr/bin/python3' | cat - bin/$@.zip > $@
	chmod 700 $@

clean:
	$(RM) -r __pycache__/ adjustkeys adjustkeys.zip
.PHONY: clean

run: adjustkeys
	python3 $<
.PHONY: run
