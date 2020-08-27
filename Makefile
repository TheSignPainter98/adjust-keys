#!/usr/bin/make

.DEFAULT_GOAL := all
SHELL = /usr/bin/bash

ADJUST_KEYS_SRCS = $(shell ./deps adjustkeys/adjustkeys.py) adjustkeys/version.py
DIST_CONTENT = adjustkeys-bin $(foreach dir,$(shell ls profiles),profiles/$(dir)/centres.yml) $(wildcard profiles/**/*.obj) $(wildcard examples/*) examples/opts.yml README.md LICENSE requirements.txt adjustkeys.1.gz adjustkeys.html ChangeLog.md adjustkeys_command_line_manual.pdf adjustkeys_yaml_manual.pdf
BLENDER_ADDON_CONTENT = $(ADJUST_KEYS_SRCS) $(foreach dir,$(shell ls profiles),profiles/$(dir)/centres.yml) $(wildcard profiles/**/*.obj) $(wildcard examples/*) examples/opts.yml README.md LICENSE requirements.txt ChangeLog.md adjustkeys_yaml_manual.pdf adjustkeys_addon.py devtools.py

all: adjustkeys-bin
.PHONY: all

ifndef NO_CYTHON
define runCython
	cython3 -X language_level=3 $^
endef
endif

define mkTargetDir
	@mkdir -p $(@D)
endef

%.1.gz: %.1
	gzip -kf $<

adjustkeys_command_line_manual.pdf: adjustkeys.1
	groff -man -Tpdf -fH < $< > $@

adjustkeys_yaml_manual.pdf: adjustkeys.1 man-wrap.awk yaml-usage.awk
	(awk -f man-wrap.awk | awk -f yaml-usage.awk | grep -v '^$$' | groff -man -Tpdf -fH) < $< > $@

adjustkeys.html: adjustkeys.1
	groff -man -Thtml < $< > $@

%.1: bin/%
ifndef NO_HELP2MAN
	(echo '.ad l' && help2man -N --no-discard-stderr ./$<) > $@
else
	echo 'Distributable compiled without help2man' > $@
endif

adjustkeys/version.py:
	(echo '# Copyright (C) Edward Jones&version: str = "$(VERSION)"' | tr '&' '\n') > $@

dist: adjust-keys.zip adjust-keys-blender-addon.zip
.PHONY: dist

adjust-keys-blender-addon.zip: $(BLENDER_ADDON_CONTENT)
	mkdir -p adjust_keys_blender_addon
	cp --parents $^ adjust_keys_blender_addon/
	# echo 'bl_info = {}' > adjust_keys_blender_addon/__init__.py
	# echo 'from .adjustkeys_addon import bl_info' > adjust_keys_blender_addon/__init__.py
	cp adjust_keys_blender_addon/adjustkeys_addon.py adjust_keys_blender_addon/__init__.py
	zip -q -MM $@ $(foreach file,$^,adjust_keys_blender_addon/$(file)) adjust_keys_blender_addon/__init__.py
	touch $@
	echo $^

adjust-keys.zip: $(DIST_CONTENT)
	zip -q -MM $@ $^
	touch $@

adjustkeys-bin: $(ADJUST_KEYS_SRCS)
	$(RM) -r bin_$(@F)/
	$(mkTargetDir)
	$(runCython)
	mkdir bin_$(@F)
	cp --parents $^ adjustkeys/adjustkeys_shell_script_main.py bin_$(@F)
	cp bin_$(@F)/adjustkeys/adjustkeys_shell_script_main.py bin_$(@F)/__main__.py
	touch bin_$(@F)/adjustkeys/__init__.py
	cd bin_$(@F)/ && zip -q -MM $(@F).zip $^ adjustkeys/__init__.py __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$(@F)/$(@F).zip > $@
	chmod 700 $@

examples/opts.yml: opts-header.txt adjustkeys-bin
	(sed 's/^/# /' | sed 's/ $$//'&& echo && ./adjustkeys-bin '-#' | grep -v opt_file) < $< > $@

requirements.txt: $(ADJUST_KEYS_SRCS)
	(pipreqs --force --print 2>/dev/null | grep -v bpy) > $@

ChangeLog.md: change-log.sh change-log-format.awk
	./$< > $@

adjustkeys_addon.py: adjustkeys_addon.py.in args.py propgen.py
	./propgen.py < $< > $@

profiles/%/centres.yml: profiles/%/centres.csv centres.yml.in centres.awk
	(awk -F, -f centres.awk | m4 -P - centres.yml.in) < $< > $@

%.yml:
	@# Do nothing
profiles/%/%.obj:
	@# Do nothing
examples/%:
	@# Do nothing
%.md:
	@# Do nothing
LICENSE:
	@# Do nothing
opts-header.txt:
	@# Do nothing


clean:
	$(RM) -r bin_*/ __pycache__/ bin/ *.c *.zip *.1.gz requirements.txt *.1 *.html ChangeLog.md examples/opts.yml adjust-keys.zip *.pdf $(wildcard profiles/**/centres.yml) adjust_keys_blender_addon/
.PHONY: clean
