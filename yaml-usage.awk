#!/usr/bin/awk -f

!/opts\.yml/ && match($0, /[^ ]*)$/) {
	key_str = substr($0, RSTART, RLENGTH - 1)
	match($0, /, yaml(..)?option(..)?file(..)?key: [^ ]*)$/)
	desc = substr($0, 0, length($0) - RLENGTH) ")"
	opt_map[key_str] = desc
	next
}

!/opts\.yml/ && !/show this help message and exit/ && !/^\.TP/

END {
	asorti(opt_map, sorted_opt_map_keys)
	for (key in sorted_opt_map_keys)
		print ".TP\n\\fB" sorted_opt_map_keys[key] "\\fR\n" opt_map[sorted_opt_map_keys[key]]
}
