# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

_DEFAULT_TEMPLATE_NAME = 'faim-huygens-template'


class MicroscopeType(Enum):
    SPINNING_DISK = 'nipkow'
    CONFOCAL = 'confocal'


class PSFMode(Enum):
    """PSF Mode (only 'auto' supported currently)"""
    AUTOMATIC = 'auto'


class ImagingDirection(Enum):
    UPWARD = 'upward'


class ExportFormat(Enum):
    HDF5 = 'hdf5'
    HDF5_UNCOMPRESSED = 'hdf5uncompr'
    ICS = 'ics'
    ICS2 = 'ics2'
    OME_TIFF = 'ometiff'
    OME_XML = 'ome'
    IMARIS = 'imaris'


class Microscopy(BaseModel):
    """Microscopy metadata."""
    micr: MicroscopeType = MicroscopeType.SPINNING_DISK  # only spinning-disk supported so far
    n_channels: int = 1  # 2
    ex: List[int] = [488]  # [488, 561]
    em: List[int] = [515]  # [515, 590]
    na: float = 1.4
    ril: float = 1.515  # Objective RI
    ri: float = 1.443  # Sample Medium RI
    pr: float = 1250  # pinhole radius
    ps: float = 24.98  # pinhole spacing
    imaging_dir: ImagingDirection = ImagingDirection.UPWARD
    "Imaging direction"
    scale_x: float = None
    scale_y: float = None
    scale_z: float = None
    scale_t: float = 0


class Deconvolution(BaseModel):
    psf_mode: PSFMode = PSFMode.AUTOMATIC  # only auto supported so far
    it: int = 20
    q: float = 0.01


_FORMAT_EXTENSIONS = {
    ExportFormat.HDF5: '.h5',
    ExportFormat.HDF5_UNCOMPRESSED: '.h5',
    ExportFormat.ICS: '.ics',
    ExportFormat.ICS2: '.ics',
    ExportFormat.OME_TIFF: '.ome.tiff',
    ExportFormat.OME_XML: '.ome.xml',
    ExportFormat.IMARIS: '.ims',
}


def create_config(input_files: List[str] = ['/path/to/input_image.ome.tif'],
                  result_dir: str = '/path/to/resultDir',
                  export_format: ExportFormat = ExportFormat.ICS,
                  microscopy_params: Microscopy = Microscopy(),
                  deconvolution_params: Deconvolution = Deconvolution(),
                  logger=logging) -> dict:
    output_paths = []
    extension = _FORMAT_EXTENSIONS[export_format]
    result = {
        'info': {
            'title': 'Batch processing template (faim-huygens)',
            'version': '2.6',
            'templateName': _DEFAULT_TEMPLATE_NAME,
            'date': datetime.now().strftime('%a %b %d %H:%M:%S %Y'),
        },
        'taskList': ['setEnv'],
        'setEnv': {
            'resultDir': result_dir,
            'perJobThreadCnt': 'auto',
            'concurrentJobCnt': '1',
            'OMP_DYNAMIC': '1',
            'timeOut': '100000',
            'exportFormat': {
                'type': export_format.value,
                'multidir': '0',
                'cmode': 'scale',
            },
            'inputConversion': 'int',
            'attemptGpu': '0',
            'useMultiGpu': '0',
            'gpuDevice': '0',
            'retainProcess': 'false',
        },
    }
    for pos, input_file in enumerate(input_files):
        logger.info(f"Adding image {pos + 1} to the workflow template.")
        workflow_id = 'workflowID:' + str(pos)
        result['taskList'].append(workflow_id)
        result[workflow_id] = {
            'info': {
                'state': 'readyToRun',
                'tag': {
                    'setp': 'none',
                    'decon': 'none',
                },
                'timeStartAbs': '0',
                'timeOut': '100000',
            },
            'taskList': ['imgOpen', 'setp'],
            'imgOpen': {
                'path': input_file,
                'series': 'off',
                'index': '0',
                'type': 'load',
            },
            'setp': _create_setp(microscopy_params),
            'imgSave': {
                'rootName': [Path(input_file).stem],
                'alsoSaveMip': '0',
                'timeOut': '10000',
            },
        }
        for c in range(microscopy_params.n_channels):
            cmle_id = 'cmle:' + str(c)
            result[workflow_id]['taskList'].append(cmle_id)
            result[workflow_id][cmle_id] = _create_cmle(deconvolution_params)

        result[workflow_id]['taskList'].append('imgSave')

        out_path = Path(result_dir, Path(input_file).stem + extension)
        output_paths.append(out_path)

    return output_paths, result


def _create_setp(params: Microscopy) -> dict:
    n = params.n_channels
    return {
        's': [params.scale_x, params.scale_y, params.scale_z, params.scale_t],
        'userDefConfidence': 'reported',
        'micr': [params.micr.value] * n,
        'parState,micr': ['verified'] * n,
        'na': [params.na] * n,
        'parState,na': ['verified'] * n,
        'ex': params.ex,
        'parState,ex': ['verified'] * n,
        'em': params.em,
        'parState,em': ['verified'] * n,
        'ril': [params.ril] * n,
        'parState,ril': ['verified'] * n,
        'ri': [params.ri] * n,
        'parState,ri': ['verified'] * n,
        'pr': [params.pr] * n,
        'parState,pr': ['verified'] * n,
        'ps': [params.ps] * n,
        'parState,ps': ['verified'] * n,
        'imaging_dir': [params.imaging_dir.value] * n,
        'parState,imaging_dir': ['verified'] * n,
    }


def _create_cmle(params: Deconvolution) -> dict:
    return {
        'psfMode': params.psf_mode.value,
        'psfPath': {},
        'mode': 'fast',
        'it': params.it,
        'q': params.q,
        'pad': 'auto',
        'bgMode': 'auto',
        'bgRadius': '0.7',
        'blMode': 'auto',
        'brMode': 'auto',
        'varPsf': 'auto',
        'varPsfCnt': '1',
        'reduceMode': 'auto',
        'acuityMode': 'off',
        'acuity': '0',
        'bg': '0.0',
        'timeOut': '10000',
    }
