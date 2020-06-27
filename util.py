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
from log import die


##
# @brief Concatenate a pair of lists (pure)
#
# @param a:list A list
# @param b:list Another list
#
# @return The concatenation of `a` and `b`
def concat(a: list, b: list) -> list:
    return a + b


##
# @brief Compute the intersection of a pair of same-type lists
#
# @param a:list A list
# @param b:list Another list
#
# @return The list containing all the items present in both `a` and `b`
def list_intersection(a: list, b: list) -> list:
    return [x for x in a if x in b]


##
# @brief The inner join of a pair of lists of dictionaries using a pair of keys.
# Outputs the list of unions of dictionaries in the input lists which share the same values at the specified keys
#
# @param las:[dict] A  list of dictionaries
# @param ka:object A key present in all of `las` used to join by equality
# @param lbs:[dict] Another list of dictionaries
# @param kb:object A key present in all of `lbs` used to join by equality
#
# @return A list of united, equal-key dictionaries [union(la, lb) | ls <- las, lb <- lbs, la[ka] == lb[kb]]
def inner_join(las: [dict], ka: object, lbs: [dict], kb: object) -> [dict]:
    if las == [] or lbs == []:
        return []
    else:
        return list(
            reduce(
                concat,
                list(
                    map(
                        lambda la:
                        [dict_union(la, lb) for lb in lbs if la[ka] == lb[kb]],
                        las))))


##
# @brief Output the union of a pair of dictionaries
#
# @param a:dict A dictionary
# @param b:dict Another dictionary
#
# @return The union of `a` and `b`, where a key is present in both, the value from `b` is used
def dict_union(a: dict, b: dict) -> dict:
    return dict(a, **b)


##
# @brief Replace some key with another while preserving the value
#
# @param a:dict A dictionary
# @param k1:object The old key
# @param k2:object The new key
#
# @return The value of `a` with (k1,v) removed and (k2,v) united for v in ran(a)
def key_subst(a: dict, k1: object, k2: object) -> dict:
    t = rem(a, k1)
    t[k2] = a[k1]
    return t


##
# @brief Remove some key from `d` and return the result
#
# @param d:dict A dictionary
# @param k A key to remove
#
# @return A copy of `d` with (k,v) removed
def rem(d: dict, k) -> dict:
    if k not in d:
        die(f'Key {k} not in {d}')
    t = dict(d)
    del t[k]
    return t


##
# @brief Return a copt of a dictionary with a particular key removed if present
#
# @param d:dict A dictionary
# @param k A key possibly in `d`
#
# @return `d` without the entry at `k` if `k` is in `d`, otherwise `d`
def rob_rem(d: dict, k) -> dict:
    t = dict(d)
    if k in t:
        del t[k]
    return t


##
# @brief Compute the difference between a pair of lists
#
# @param a:list A list
# @param b:list Another list
#
# @return `a` \ `b`
def list_diff(a: list, b: list) -> list:
    return [x for x in a if x not in b]
