#!/bin/bash

echo "# Change Log"
git log --pretty=format:'%d@%s' \
  | grep -vEe '^(\(*.*\))*@Merge branch' \
  | grep -v '^@Initial commit' \
  | uniq \
  | awk -F')' -f change-log-format.awk
