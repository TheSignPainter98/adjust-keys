from .input_types import type_check_colour_map
from .log import die, printe
from .util import dict_union
from .yaml_io import read_yaml
from collections import OrderedDict
from functools import partial
from pyparsing import infixNotation, Literal, oneOf, opAssoc, ParserElement, ParseException, pyparsing_common, Word
from sys import getrecursionlimit, setrecursionlimit, stderr
from typing import Callable, Iterator, List, Tuple

LOWER_RECURSION_LIMIT:int = 3000

uniops:OrderedDict = OrderedDict([
        ('+', lambda v: v),
        ('-', lambda v: -v),
    ])
binops:OrderedDict = OrderedDict([
        ('^^', lambda a,b: a ** b),
        ('*', lambda a,b: a * b),
        ('/', lambda a,b: a / b),
        ('//', lambda a,b: a // b),
        ('%', lambda a,b: a % b),
        ('+', lambda a,b: a + b),
        ('-', lambda a,b: a - b),
    ])
compops:OrderedDict = OrderedDict([
        ('<', lambda a,b: a < b),
        ('<=', lambda a,b: a <= b),
        ('>', lambda a,b: a > b),
        ('>=', lambda a,b: a >= b),
        ('=', lambda a,b: a == b),
        ('==', lambda a,b: a == b),
        ('!=', lambda a,b: a != b),
    ])
logicuniops:OrderedDict = OrderedDict([
        ('!', lambda c: not c),
    ])
logicbinops:OrderedDict = OrderedDict([
        ('&', lambda c1,c2: c1 and c2),
        ('|', lambda c1,c2: c1 or c2),
        ('^', lambda c1,c2: c1 ^ c2),
        ('=>', lambda c1,c2: not c1 or c2),
        ('<=>', lambda c1,c2: bool(c1) == bool(c2)),
    ])
ops = dict_union(uniops, binops, compops, logicuniops, logicbinops)

def parse_colour_map(fname:str) -> [dict]:
    raw_map:[dict] = read_yaml(fname)

    if not type_check_colour_map(raw_map):
        die('Colour map failed type-checking, see console for more information')

    mappings:[Tuple[str, str, Callable]] = [
        ('key-pos', 'parsed-key-pos', parse_equation),
        ('key-name', 'key-name', sanitise_key_name),
    ]
    colour_map:[dict] = raw_map
    for mappingInf in mappings:
        colour_map = recursively_add(*mappingInf, colour_map)

    return list(colour_map)

def sanitise_key_name(rule:dict) -> dict:
    if 'key-name' in rule and type(rule['key-name']) == str:
        rule['key-name'] = [rule['key-name']]
    return rule

def parse_equation(eq:str) -> dict:
    ParserElement.enablePackrat()

    if getrecursionlimit() < LOWER_RECURSION_LIMIT:
        setrecursionlimit(LOWER_RECURSION_LIMIT)

    # Define atoms
    NUM = pyparsing_common.number
    VARIABLE = Word(['x', 'y', 'X', 'Y'], exact=True)
    operand = NUM | VARIABLE

    # Define production rules
    expr = infixNotation(operand,
            [ (Literal(op), 1, opAssoc.RIGHT, op_rep) for op in uniops ]
            + [ (Literal(op), 2, opAssoc.LEFT, op_rep) for op in binops ]
        )
    comp = infixNotation(expr,
            [ (Literal(op), 2, opAssoc.LEFT, op_rep) for op in compops ]
        )
    cond = infixNotation(comp,
            [ (Literal(op), 1, opAssoc.RIGHT, op_rep) for op in logicuniops ]
            + [ (Literal(op), 2, opAssoc.LEFT, op_rep) for op in logicbinops ]
        )

    try:
        return cond.parseString(eq, parseAll=True)[0]
    except ParseException as pex:
        printe('Error while parsing "%s": %s' %(eq, str(pex)))
        return None

def op_rep(_1:str, _2:int, toks:List[object]) -> dict:
    toks = toks[0]
    op:str
    op_args:[object]
    if len(toks) == 2:
        op = toks[0]
        op_args = [toks[1]]
    elif len(toks) == 3:
        op = toks[1]
        op_args = [toks[0], toks[2]]
    else:
        printe('Unknown number of tokens: %d in %s' %(len(toks), list(map(str, toks))))
        exit(1)
    return {
        'op': ops[op],
        'pretty-op': op,
        'args': op_args,
    }

def recursively_add(old_key:str, new_key:str, f:Callable, data:object) -> object:
    rules:dict = {
        dict: lambda d: dict_union(
            {
                k: (recursively_add(old_key, new_key, f, v) if k != old_key else v)
                    for k,v in d.items()
            },
            { new_key: f(d[old_key]) }
                if old_key in d else {}
        ),
        float: lambda f: f,
        int: lambda i: i,
        list: lambda l: list(map(lambda e: recursively_add(old_key, new_key, f, e), data)),
        str: lambda s: s,
        type(None): lambda n: n,
        type(lambda:None): lambda f: f,
    }
    return rules[type(data)](data)
