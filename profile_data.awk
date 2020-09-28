#!/usr/bin/awk -MF, -f

BEGIN {
	unit_length = 19.05
	if (!margin_offset) {
		print "Please specify a margin_offset" >"/dev/stderr"
		exit 1
	}
}

# Ignore header
NR == 1 {
	next
}

# Compute and output the centres as m4 code
{
	# Resolve label name
	label = toupper($1)
	gsub("-", "_", label)

	# Compute unit fraction offset
	cap_boundary = $2
	cap_centre = $3
	inside_cap_offset = cap_boundary - cap_centre
	space_offset = margin_offset + inside_cap_offset
	if (space_offset < 0)
		space_offset *= -1

	# Output
	printf "m4_define(`%s', `%.7f')m4_dnl\n", label, space_offset
}
