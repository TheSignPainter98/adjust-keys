#!/usr/bin/make

.DEFAULT_GOAL := all
SHELL = bash

ADJUST_KEYS_SRCS = $(shell ./deps.py adjustkeys/adjustkeys.py) adjustkeys/version.py
DEVEL_SRCS = adjustkeys-bin $(foreach dir,$(shell ls profiles),profiles/$(dir)/profile_data.yml)
DIST_CONTENT = $(DEVEL_SRCS) $(wildcard profiles/**/*.obj) $(wildcard glyphs/**/*.svg) $(wildcard examples/*) examples/opts.yml README.md LICENSE requirements.txt adjustkeys.1.gz adjustkeys.html ChangeLog.md adjustkeys_command_line_manual.pdf adjustkeys_yaml_manual.pdf
BLENDER_ADDON_SRCS = $(shell ./deps.py adjustkeys/adjustkeys_addon.py.in)
BLENDER_ADDON_CONTENT = $(BLENDER_ADDON_SRCS) $(foreach dir,$(shell ls profiles),profiles/$(dir)/profile_data.yml) $(wildcard profiles/**/*.obj) $(wildcard glyphs/**/*.svg) $(wildcard examples/*) examples/opts.yml README.md LICENSE requirements.txt ChangeLog.md adjustkeys_yaml_manual.pdf adjustkeys/adjustkeys_addon.py adjustkeys/devtools.py

all: adjustkeys-bin
.PHONY: all

ifndef NO_CYTHON
define runCython
	cython3 -X language_level=3 $(subst \,/,$(filter %.py,$^))
	@$(RM) $(subst \,/,$(patsubst %.py,%.c,$(filter %.py,$^)))
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

%.1: %-bin
ifndef NO_HELP2MAN
	(echo '.ad l' && help2man -N --no-discard-stderr ./$<) > $@
else
	echo 'Distributable compiled without help2man' > $@
endif

adjustkeys/version.py:
	(echo '# Copyright (C) Edward Jones&version: str = "$(VERSION)"' | tr '&' '\n') > $@

devel: adjustkeys-bin
.PHONY: devel

dist: adjust-keys.zip adjust-keys-blender-addon.zip ChangeLog.md
.PHONY: dist

adjust-keys-blender-addon.zip: $(BLENDER_ADDON_CONTENT)
	$(runCython)
	mkdir -p adjust_keys_blender_addon
	mkdir -p $(subst \,/,$(sort $(foreach f,$^,"adjust_keys_blender_addon/$(dir $f)")))
	cp --parents $(subst \,/,$(foreach file,$^,"$(file)")) adjust_keys_blender_addon/
	cp adjust_keys_blender_addon/adjustkeys/adjustkeys_addon.py adjust_keys_blender_addon/__init__.py
	zip -q -MM $@ $(subst \,/,$(foreach file,$^,"adjust_keys_blender_addon/$(file)")) adjust_keys_blender_addon/__init__.py
	touch $@

adjust-keys.zip: $(DIST_CONTENT)
	zip -q -MM $@ $(subst \,/,$(foreach file,$^,"$(file)"))
	touch $@

adjustkeys-bin: $(ADJUST_KEYS_SRCS)
	$(RM) -r bin_$(@F)/
	$(mkTargetDir)
	$(runCython)
	mkdir bin_$(@F)
	mkdir -p $(subst \,/,$(sort $(foreach f,$^,"bin_$(@F)/$(dir $f)")))
	cp --parents $(subst \,/,$^) adjustkeys/adjustkeys_shell_script_main.py bin_$(@F)
	cp bin_$(@F)/adjustkeys/adjustkeys_shell_script_main.py bin_$(@F)/__main__.py
	touch bin_$(@F)/adjustkeys/__init__.py
	touch bin_$(@F)/__init__.py
	cd bin_$(@F)/ && zip -q -MM $(@F).zip $(subst \,/,$^) adjustkeys/__init__.py __main__.py && cd ../
	echo '#!/usr/bin/python3' | cat - bin_$(@F)/$(@F).zip > $@
	chmod 700 $@

examples/opts.yml: opts-header.txt adjustkeys-bin
	((sed 's/^/# /' && ./adjustkeys-bin '-#') | sed 's/ $$//' | grep -v opt_file | sed 's/print_opts_yml: true/print_opts_yml: false/') < $< > $@

requirements.txt: $(ADJUST_KEYS_SRCS)
	@# Assumes that Blender is already installed and has mathutils available
	(pipreqs --force --print 2>/dev/null | grep -v bpy | grep -v mathutils) > $@

ChangeLog.md: change-log.sh change-log-format.awk
	./$< > $@

adjustkeys/adjustkeys_addon.py: adjustkeys/adjustkeys_addon.py.in adjustkeys/args.py addongen $(ADJUST_KEYS_SRCS)
	./addongen adjustkeys/adjustkeys.py < $< > $@

profiles/%/profile_data.yml: profiles/%/profile_data.csv profiles/%/profile_data.yml.in profile_data.awk
	(awk -F, -f profile_data.awk -v unit_length=$$(yq -y .unit_length <$(word 2, $^) | head -n 1) | m4 -P - $(word 2, $^)) < $< > $@

adjustkeys/args.py:
	@# Do nothing
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
	$(RM) -r bin_*/ $(wildcard **/__pycache__/) bin/ *.c *.zip *.1.gz requirements.txt *.1 *.html ChangeLog.md examples/opts.yml adjust-keys.zip *.pdf $(wildcard profiles/**/profile_data.yml) adjust_keys_blender_addon/ adjustkeys/adjustkeys_addon.py adjustkeys-bin
.PHONY: clean
