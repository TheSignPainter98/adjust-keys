#!/bin/bash

echo "# Change Log"
git log --pretty=format:'%d@%s' \
	| grep -vEe '^(\(*.*\))*@Merge' \
	| grep -v '^@Initial commit' \
	| grep -vEi '\(user devices (not |un)affect?ed' \
	| uniq \
	| awk -F')' -f change-log-format.awk
