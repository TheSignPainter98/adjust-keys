# Copyright (C) Edward Jones

from decimal import Decimal
from functools import reduce
from .log import die


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
# @brief Concatenate a pair of lists by mutating the first (impure)
#
# @param a:list A list
# @param b:list Another list
#
# @return The concatenation of `a` and `b`; `a` is now equal to the concatenation of the original values
def iconcat(a: list, b:list) -> list:
    a.extend(b)
    return a


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

    if cond is None:
        cond = eq

    return list(
        reduce(
            concat,
            list(
                map(
                    lambda la: [
                        dict_union(la, lb) for lb in lbs
                        if cond(safe_get(la, ka), safe_get(lb, kb))
                    ], las))))


def left_outer_join(las:[dict], ka:object, lbs:[dict], kb:object, cond=None) -> [dict]:
    if las == []:
        return []
    elif lbs == []:
        return las

    if cond is None:
        cond = eq

    return inner_join(las, ka, lbs, kb, cond=cond) + list(filter(lambda la: not any(map(lambda lb: cond(la[ka], lb[kb]), lbs)), las))


def right_outer_join(las:[dict], ka:object, lbs:[dict], kb:object, cond=None) -> [dict]:
    if lbs == []:
        return []
    elif las == []:
        return lbs

    if cond is None:
        cond = eq

    return inner_join(las, ka, lbs, kb, cond=cond) + list(filter(lambda lb: not any(map(lambda la: cond(la[ka], lb[kb]), las)), lbs))


def eq(a: object, b: object) -> bool:
    return a == b


##
# @brief Output the union of a pair of dictionaries
#
# @param ds:dict A dictionary
#
# @return The union of `a` and `b`, where a key is present in both, the value from `b` is used
##
# @brief Output the unoin of a list of dictionaries
#
# @param *ds:[dict] A list of dictionaries
#
# @return The union of all ds
def dict_union(*ds:[dict]) -> dict:
    def _dict_union(a:dict, b:dict) -> dict:
        return dict(a, **b)
    return dict(reduce(_dict_union, ds, {}))


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
    if a is None:
        return None
    elif type(a) == list:
        return a[i] if len(a) > i else None
    elif type(a) == dict:
        return a[i] if i in a else None
    else:
        die('Can\'t safely-get from unhandled type %s (more code is needed in %s)'
            % (type(a), __file__))


def flatten_list(lst:list) -> list:
    if type(lst) != list and type(lst) != tuple:
        return [lst]
    else:
        return list(reduce(concat, map(flatten_list, lst), []))

def get_only(lst:[object], empty_message:str, plural_message:str) -> object:
    if lst == []:
        die(empty_message)
    elif len(lst) > 1:
        die(plural_message % (len(lst), lst))
    else:
        return lst[0]

def get_dicts_with_duplicate_field_values(data:[dict], key:object) -> dict:
    seens:dict = {}
    for datum in data:
        value:object = datum[key]
        if value in seens:
            seens[value].append(datum)
        else:
            seens[value] = [datum]
    return { p:seens[p] for p in seens if len(seens[p]) > 1 }

def dumb_wrap_text(text:[str], width:int) -> [str]:
    indentText:str = '    '
    bulletText:str = '∙ '

    def indent(p:tuple) -> str:
        parInd:int = p[0]
        parText:str = p[1]

        if parInd:
            if parText.startswith(bulletText):
                parText = indentText[:-len(bulletText)] + parText
            else:
                parText = indentText + parText
        return parText

    indentedText:[str] = map(indent, enumerate(text))

    def clean_line(line:str) -> str:
        if line.startswith(indentText) or line.startswith(indentText[:-len(bulletText)]):
            return line
        else:
            return line.strip()

    def dumb_wrap_paragraph(para:str, width:int) -> [str]:
        spaceIndices:[int] = [ pos for (pos,char) in enumerate(para) if char == ' ' ]
        splitPara:[str] = []
        currIndex:int = 0
        currLen:int = 0
        prevSpaceIndex:int = 0
        for spaceIndex in spaceIndices:
            if spaceIndex - currIndex > width:
                # Break
                splitPara.append(clean_line(para[currIndex:prevSpaceIndex]))
                currIndex = prevSpaceIndex
            prevSpaceIndex = spaceIndex
        if len(para) - 1 - currIndex > width:
            splitPara.append(clean_line(para[currIndex:spaceIndex]))
            splitPara.append(clean_line(para[spaceIndex:]))
        else:
            splitPara.append(clean_line(para[currIndex:]))

        return splitPara

    return list(reduce(iconcat, map(lambda l: dumb_wrap_paragraph(l, width), indentedText)))

def frange(x, y, jump):
    x = Decimal(x)
    y = Decimal(y)
    jump = Decimal(jump)
    while x <= y:
        yield float(x)
        x += jump

def layout_is_wider_than_height(v:'Vector') -> bool:
    return v[0] <= 0.5 * v[1]
