#!/usr/bin/python3

from args import configurable_args
from math import ceil, log10
from sys import stdin

def prop(a:dict) -> str:
    atype:type = a['type']
    label:str = '"' + a['label'] + '"'
    description:str = '"' + a['help'] + '"'
    default = a['default'] if a['type'] != str else '"' + a['default'] + '"'
    if 'choices' in a:
        choices:[[str, str, str, int]] = []
        rawChoices = a['choices']
        for i in range(len(rawChoices)):
            choice = rawChoices[i]
            choices.append((choice.upper().replace('-', '_'), choice.title(), '', i))
        default = default.upper().replace('-', '_')
        return f'EnumProperty(items={choices}, name={label}, default={default}, description={description})'
    elif atype == bool:
        return f"BoolProperty(name={label}, description={description}, default={default})"
    elif atype == float:
        soft_min:float = a['soft-min']
        soft_max:float = a['soft-max']
        fractional_default:float = float(a['default']) % 1.0
        precision:int = min(5, max(1, ceil(-log10(fractional_default)) + 2 if fractional_default != 0 else 0))
        return f"FloatProperty(name={label}, description={description}, default={default}, soft_min={soft_min}, soft_max={soft_max}, precision={precision})"
    elif atype == int:
        minval:float = a['min']
        maxval:float = a['max']
        return f"IntProperty(name={label}, description={description}, default={default}, min={minval}, max={maxval})"
    elif atype == str:
        if 'str-type' in a:
            str_type:str = a['str-type']
            if str_type == 'file':
                return f"StringProperty(name={label}, description={description}, default={default}, subtype='FILE_PATH')"
            elif str_type == 'dir':
                return f"StringProperty(name={label}, description={description}, default={default}, subtype='DIR_PATH')"
            else:
                die('Unknown string property subtype: "%s"' % str_type)
        else:
            return f"StringProperty(name={label}, description={description}, default={default})"


def ident(x:object) -> object:
    return x
props:str = '\n    '.join(list(map(lambda a: a['dest'] + ':' + prop(a), configurable_args)))

print(stdin.read().replace('KCZA_CUSTOM_PROPERTIES', props))
