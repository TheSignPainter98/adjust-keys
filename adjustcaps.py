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

from layout import parse_layout
from log import init_logging
from obj_io import read_obj, write_obj
from os import walk
from os.path import basename, exists, join
from yaml_io import read_yaml


def adjust_caps(verbosity:int, unit_length:float, global_x_offset:float, global_y_offset:float, profile_file:str, cap_dir:str, layout_file:str, layout_row_profile_file:str) -> str:
    init_logging(verbosity)
    layout_row_profiles: [str] = read_yaml(layout_row_profile_file)
    layout: [dict] = parse_layout(layout_row_profiles, read_yaml(layout_file))
    caps:[dict] = get_caps(cap_dir)
    write_obj('-', caps[0]['cap-obj'])

    return 'asdf'

def get_caps(cap_dir:str) -> [dict]:
    capFiles:[str] = []
    for (root, _, fnames) in walk(cap_dir):
        capFiles += list(map(lambda f: join(root, f), list(filter(lambda f:f.endswith('.obj'), fnames))))
    return list(map(lambda c: { 'cap-name': basename(c)[:-4], 'cap-obj': read_obj(c) }, capFiles))

def gen_cap_file_name(cap_loc:str, cap:dict) -> str:
    return (join(cap_loc, cap['profile-part'] + '_' + cap['width']) if 'key-type' not in cap else cap['key-type']) + '.obj'
