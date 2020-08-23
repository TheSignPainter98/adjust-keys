#!/usr/bin/awk -f

BEGIN {
	currLine
}

$1 ~ /^\./ {
	print currLine
	print
	currLine = ""
	next
}

currLine != "" {
	currLine = currLine " " $0
	next
}

currLine == "" && $1 !~ /^\\/ {
	currLine = $0
}

END {
	if ($1 !~ /^\./)
		print currLine
}
