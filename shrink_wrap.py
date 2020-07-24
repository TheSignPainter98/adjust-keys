# Copyright (C) Edward Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from log import printi

def shrink_wrap_glyphs_to_keys(glyph_names:[str], keycap_model_name:str) -> None:
    # Shrink-wrap glyphs onto the keycaps
    # TODO: shrink-wrap once scaled!
    printi('Shrink-wrapping glyphs onto "%s"' % keycap_model_name)
    pass
