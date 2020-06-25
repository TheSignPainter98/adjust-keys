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

from functools import reduce

def append(a:list, b:list) -> list:
    return a + b

def list_intersection(a:list, b:list) -> list:
    return [x for x in a if x in b]

def nat_join(las:[dict], lbs:[dict], key:object) -> [dict]:
    return list(reduce(append, list(map(lambda la: [dict_union(la, lb) for lb in lbs if la[key] == lb[key]], las))))

def dict_union(a:dict, b:dict) -> dict:
    return dict(a, **b)

def rem(d:dict, k) -> dict:
    if k not in d:
        die(f'Key {k} not in {d}')
    t = dict(d)
    del t[k]
    return t
