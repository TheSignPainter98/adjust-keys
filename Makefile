#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_KEYS_SRCS = $(shell ./deps adjustkeys.py)
DIST_CONTENT = adjustkeys $(wildcard profiles/kat/*.obj profiles/kat/*.yml) $(wildcard examples/*) README.md LICENSE pkgs.txt adjustkeys.1.gz

all: adjustkeys
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
ifndef NO_HELP2MAN
	(help2man -N --no-discard-stderr ./$< | gzip - -) > $@
else
	echo 'Disctributable compiled without help2man' > $@
endif

dist: adjust-keys.zip
.PHONY: dist

adjust-keys.zip: $(DIST_CONTENT)
	zip -q -o $@ $^

adjustkeys: $(ADJUST_KEYS_SRCS)
	$(compilePython)

pkgs.txt: $(ADJUST_KEYS_SRCS)
	pip3 freeze > $@

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
	$(RM) -r bin_*/ __pycache__/ adjustkeys *.c *.zip *.1.gz
.PHONY: clean
