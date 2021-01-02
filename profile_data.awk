#!/usr/bin/awk -MF, -f

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

	# Output
	printf "m4_define(`%s', `%.7f')m4_dnl\n", label, inside_cap_offset
}
