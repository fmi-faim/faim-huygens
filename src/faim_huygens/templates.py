# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import List, Union

from pyparsing import OneOrMore, Word, nestedExpr, printables, restOfLine

KNOWN_DICT_KEYS = ['info', 'exportFormat']


def parse_file(template_file: Path) -> List[Union[str, list]]:
    with open(template_file) as f:
        return parse_string(f.read())


def parse_string(template: str) -> List[Union[str, list]]:
    line = Word(printables) + nestedExpr('{', '}')
    line.ignore("#" + restOfLine)
    lines = OneOrMore(line)
    return lines.parseString(template).asList()


def to_config_dict(tokens: list) -> dict:
    config = list_to_dict(tokens)
    dict_convert_known_keys(config)
    return config


def dict_convert_known_keys(input_dict):
    for key in input_dict:
        if key in KNOWN_DICT_KEYS or ('taskList' in input_dict.keys() and key in input_dict['taskList']):
            input_dict[key] = list_to_dict(input_dict[key])
            dict_convert_known_keys(input_dict[key])


def list_to_dict(input_list):
    return dict(zip(input_list[::2], input_list[1::2]))


def as_tcl_string(value: (Union[str, list, dict])):
    if isinstance(value, dict):
        return '{' + ' '.join([f"{key} {as_tcl_string(value[key])}" for key in value]) + '}'
    elif isinstance(value, list):
        return '{' + ' '.join([as_tcl_string(item) for item in value]) + '}'
    elif ' ' in value:
        return '{' + value + '}'
    else:
        return value


def write_template(output_file: Path, config: dict, comment: str = "Huygens template file written by faim-huygens"):
    with open(output_file, 'w') as f:
        # write multi-line comment at the beginning of output file
        f.write('# '.join(('\n' + comment).splitlines(True)))

        # write a line per dict entry
        for key in config:
            f.write(f"\n{key} {as_tcl_string(config[key])}")
