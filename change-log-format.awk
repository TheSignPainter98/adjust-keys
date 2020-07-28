#!/usr/bin/awk -F) -f

NR == 1 && $1 !~ /tag:/ {
	print "\n## _Unreleased Version_\n"
}

match($1, /tag: [^,]*/) {
	tagstr = substr($0, RSTART, RLENGTH)
	match(tagstr, /[^ ,]*$/)
	printf "\n## %s\n\n", substr(tagstr, RSTART, RLENGTH)
}

{
	sub("^[^@]*@", "", $0)
	printf "- %s\n", $0
}
