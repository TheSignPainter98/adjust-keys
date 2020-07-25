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

from blender_available import blender_available
if blender_available():
    from bpy import data, context, types

from log import printi


def shrink_wrap_glyphs_to_keys(glyph_names: [str], keycap_model_name: str,
                               cap_unit_length: float,
                               shrink_wrap_offset: float) -> None:
    # Shrink-wrap glyphs onto the keycaps
    printi('Shrink-wrapping glyphs onto "%s"' % keycap_model_name)
    for glyph_name in glyph_names:
        # Translate to favourable position (assuming no 3u tall keycaps
        glyph:Obj = data.objects[glyph_name]
        glyph.location.z += 3.0 * cap_unit_length

        #  # Shrink wrap glyph onto keycaps
        modName: str = 'shrink_wrap_' + glyph.name
        mod: ShrinkWrapModifier = glyph.modifiers.new(
            name=modName, type='SHRINKWRAP')
        mod.target = data.objects[keycap_model_name]
        mod.wrap_method = 'PROJECT'
        mod.use_project_z = True
        mod.use_negative_direction = True
        mod.offset = shrink_wrap_offset
