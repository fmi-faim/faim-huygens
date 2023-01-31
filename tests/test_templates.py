# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from faim_huygens.templates import parse_file, to_config_dict, write_template


@pytest.fixture
def template_path():
    return Path('./tests/resources/test_template.hgsb')


@pytest.fixture
def minimal_config():
    return {
        'info': {
            'title': 'Batch processing template'.split(' '),
            'version': '2.6',
        },
        'taskList': ['setEnv', 'workflowID:0'],
        'setEnv': {
            'resultDir': '/path/to/export/dir',
            'exportFormat': {
                'type': 'ics',
                'multidir': '0',
                'cmode': 'scale',
            },
        },
        'workflowID:0': {
            'taskList': ['imgOpen', 'setp', 'cmle:0', 'imgSave'],
            'info': {
                'state': 'readyToRun',
                'tag': ['setp', 'Micro', 'decon', 'Decon'],
            },
            'imgOpen': {
                'path': ['/path/to/input/image.ome.tif'],
                'series': 'off',
                'index': '0',
            },
            'setp': {
                'ex': ['561', '561', '561'],
            },
            'cmle:0': {},
            'imgSave': {
                'rootName': ['test_image_faim-huygens'],
            },
        },
    }


def test_parsing(template_path):
    config = to_config_dict(parse_file(template_path))
    assert ['setEnv', 'workflowID:0'] == config['taskList']
    assert 'cmle:0' in config['workflowID:0']['taskList']
    # TODO assert specific features
    # assert {} == config['info']
    # assert {} == config['workflowID:0']


def test_writing(tmp_path, minimal_config):
    template_path = Path(tmp_path, 'template.hgsb')
    write_template(template_path, minimal_config)
    read_config = to_config_dict(parse_file(template_path))
    assert minimal_config == read_config
