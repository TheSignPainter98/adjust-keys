#!/usr/bin/make

.DEFAULT_GOAL := all

ADJUST_KEYS_SRCS = $(shell ./deps adjustkeys.py) version.py
DIST_CONTENT = adjustkeys $(wildcard profiles/kat/*.obj profiles/kat/*.yml) $(wildcard examples/*) README.md LICENSE requirements.txt adjustkeys.1.gz adjustkeys.html ChangeLog.md

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
	cd bin_$@/ && zip -q $@.zip $(shell echo $^ | tr ' ' '\n') __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$@/$@.zip > $@
	chmod 700 $@
endef

%.1.gz: %.1
	gzip -kf $<

adjustkeys.html: adjustkeys.1
	groff -man -Thtml < $< > $@

%.1: %
ifndef NO_HELP2MAN
	help2man -N --no-discard-stderr ./$< > $@
else
	echo 'Distributable compiled without help2man' > $@
endif

version.py:
	echo -e '# Copyright (C) Edward Jones\nversion: str = "$(VERSION)"' > $@

dist: adjust-keys.zip
.PHONY: dist

adjust-keys.zip: $(DIST_CONTENT)
	zip -q -o $@ $^

adjustkeys: $(ADJUST_KEYS_SRCS)
	$(compilePython)

requirements.txt: $(ADJUST_KEYS_SRCS)
	pipreqs --force --print 2>/dev/null > $@

ChangeLog.md: change-log.sh change-log-format.awk
	./$< > $@

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
	$(RM) -r bin_*/ __pycache__/ adjustkeys *.c *.zip *.1.gz requirements.txt *.1 *.html
.PHONY: clean
