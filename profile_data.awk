#!/usr/bin/awk -MF, -f

BEGIN {
	unit_length = 19.05
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
	top = $2
	centre_face = $3
	offset = top - centre_face
	abs_offset = margin_offset + offset
	unit_offset = abs_offset / unit_length
	if (unit_offset < 0)
		unit_offset = -unit_offset

	# Output
	printf "m4_define(`%s', `%.10f')m4_dnl\n", label, unit_offset
}
