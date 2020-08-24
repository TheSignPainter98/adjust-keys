#!/usr/bin/python3

from args import configurable_args, op_args
from math import ceil, log10
from sys import stdin
from util import rem

def main() -> None:
    props:str = '\n    '.join(list(map(lambda a: a['dest'] + ':' + prop(a), configurable_args)))
    ops:[dict] = list(sorted(map(op, op_args), key=lambda op: op['label']))
    file:str = stdin.read()

    replacements:dict = {
        'KCZA_CUSTOM_PROPERTIES': props,
        'KCZA_CUSTOM_OPERATORS': '\n\n'.join(list(map(lambda op: op['src'], ops))),
        'KCZA_CUSTOM_OPERATOR_HEADERS': ', '.join(list(map(lambda op: str(rem(op, 'src')), ops))),
        'KCZA_CUSTOM_OPERATOR_TYPES': ', '.join(list(map(lambda op: op['name'], ops)))
    }

    for p in replacements.items():
        file = file.replace(p[0], p[1])
    print(file)

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

def op(arg:dict) -> dict:
    opName:str = op_name(arg['dest'])
    opIdName:str = 'object.' + opName.lower()
    opIdLabel:str = arg['label']
    return {
        'name': opName,
        'icon': arg['icon'] if 'icon' in arg else 'SCRIPT',
        'idname': opIdName,
        'label': arg['label'],
        'src': '\n'.join([
            'class %s(Operator):' % opName,
            '    ' + '\n    '.join([
                "bl_idname = '%s'" % opIdName,
                "bl_label = '%s'" % arg['label'],
                '',
                'def execute(self, context):',
                '    ' + '\n        '.join([
                    "self.report({'INFO'}, 'Adjustkeys: See system console for output')",
                    'akargs:dict = get_args_from_ui(context)',
                    "print('=' * 80)",
                    "adjustkeys(akargs, { '%s': '%s' })" % (arg['dest'], arg['short']),
                    "print('=' * 80)",
                    "return {'FINISHED'}"
                ])
            ])
        ])
    }

def op_name(dest:str) -> str:
    return 'akminiop' + dest.title().replace('_', '')


if __name__ == '__main__':
    main()
