# Copyright (C) Edward Jones

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
# @brief The inner join of a pair of lists of dictionaries using pairs of keys and a condition between them.
# Outputs the list of unions of dictionaries in the input lists which share the same values at the specified keys
#
# @param las:[dict] A  list of dictionaries
# @param ka:object A key present in all of `las` used to join by cond
# @param lbs:[dict] Another list of dictionaries
# @param kb:object A key present in all of `lbs` used to join by cond
# @param cond Specify the condition between values, or None for equality
#
# @return A list of united, equal-key dictionaries [union(la, lb) | ls <- las, lb <- lbs, la[ka] == lb[kb]]
def inner_join(las: [dict],
               ka: object,
               lbs: [dict],
               kb: object,
               cond=None) -> [dict]:
    if las == [] or lbs == []:
        return []
    else:

        def eq(a: object, b: object) -> bool:
            return a == b

        if cond is None:
            cond = eq
        return list(
            reduce(
                concat,
                list(
                    map(
                        lambda la: [
                            dict_union(la, lb) for lb in lbs
                            if cond(la[ka], lb[kb])
                        ], las))))


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


##
# @brief Safely get the value at a key from a structure or None if the structure doesn't ahve the key
#
# @param [object]
# @param object
#
# @return
def safe_get(a: [object], i: object) -> object:
    if type(a) == list:
        return a[i] if len(a) > i else None
    elif type(a) == dict:
        return a[i] if i in a else None
    else:
        die('Can\'t safely-get from unhandled type %s (more code is needed in %s)'
            % (type(a), __file__))


def flatten_list(lst:list) -> list:
    if type(lst) == str:
        return [lst]
    else:
        return list(reduce(concat, map(flatten_list, lst), []))

def get_only(lst:[object]) -> object:
    if lst == []:
        die('Attempted to get an element in an empty list')
    elif len(lst) > 1:
        die('Attempted to get "only" element in a list of size %d (expected exactly one element)' % len(lst))
    else:
        return lst[0]
