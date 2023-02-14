# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT
from pathlib import Path

import pytest
from faim_huygens.parameters import create_config, ExportFormat


@pytest.fixture
def expected_dict():
    return {'info': {'title': 'Batch processing template (faim-huygens)', 'version': '2.6',
                     'templateName': 'faim-huygens-template', 'date': 'Fri Feb 03 14:49:24 2023'},
            'taskList': ['setEnv', 'workflowID:0'],
            'setEnv': {'resultDir': '/path/to/resultDir', 'perJobThreadCnt': 'auto', 'concurrentJobCnt': '1',
                       'OMP_DYNAMIC': '1', 'timeOut': '100000',
                       'exportFormat': {'type': 'ics', 'multidir': '0', 'cmode': 'scale'}, 'inputConversion': 'int',
                       'attemptGpu': '0', 'useMultiGpu': '0', 'gpuDevice': '0', 'retainProcess': 'false'},
            'workflowID:0': {
                'info': {'state': 'readyToRun', 'tag': {'setp': 'none', 'decon': 'none'}, 'timeStartAbs': '0',
                         'timeOut': '100000'}, 'taskList': ['imgOpen', 'setp', 'cmle:0', 'imgSave'],
                'imgOpen': {'path': '/path/to/input_image.ome.tif', 'series': 'off', 'index': '0', 'type': 'load'},
                'setp': {'s': [None, None, None, 0], 'userDefConfidence': 'reported', 'micr': ['nipkow'],
                         'parState,micr': ['verified'], 'na': [1.4], 'parState,na': ['verified'], 'ex': [488],
                         'parState,ex': ['verified'], 'em': [515], 'parState,em': ['verified'], 'ril': [1.515],
                         'parState,ril': ['verified'], 'ri': [1.443], 'parState,ri': ['verified'], 'pr': [1250],
                         'parState,pr': ['verified'], 'ps': [24.98], 'parState,ps': ['verified'],
                         'imaging_dir': ['upward'], 'parState,imaging_dir': ['verified']},
                'imgSave': {'rootName': ['input_image.ome'], 'alsoSaveMip': '0', 'timeOut': '10000'},
                'cmle:0': {'psfMode': 'auto', 'psfPath': {}, 'mode': 'fast', 'it': 20, 'q': 0.01, 'pad': 'auto',
                           'bgMode': 'auto', 'bgRadius': '0.7', 'blMode': 'auto', 'brMode': 'auto', 'varPsf': 'auto',
                           'varPsfCnt': '1', 'reduceMode': 'auto', 'acuityMode': 'off', 'acuity': '0', 'bg': '0.0',
                           'timeOut': '10000'}}}


def test_create_config(expected_dict):
    out_paths, config = create_config(
        export_format=ExportFormat.ICS
    )
    print(config)
    # overwrite date to effectively ignore it
    config['info']['date'] = expected_dict['info']['date']
    assert expected_dict == config
    assert Path('/path/to/resultDir/input_image.ome.ics') == out_paths[0]
