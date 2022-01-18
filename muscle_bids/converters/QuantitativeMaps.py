import os

from .abstract_converter import Converter
from ..dosma_io import MedicalVolume
from ..utils.headers import get_raw_tag_value, group


class QT2Converter(Converter):

    @staticmethod
    def get_name():
        return 'T2'

    @staticmethod
    def get_directory():
        return 'quant'

    @staticmethod
    def get_file_name(subject_id: str):
        return os.path.join(f'{subject_id}_t2')

    @staticmethod
    def is_dataset_compatible(med_volume: MedicalVolume):
        if med_volume.ndim == 3:
            return True
        else:
            return False

    @staticmethod
    def convert_dataset(med_volume: MedicalVolume):
        med_volume_out = group(med_volume, 'EchoTime')

        # rename flip angle. Maybe Siemens-specific again?
        med_volume_out.bids_header['RefocusingFlipAngle'] = med_volume_out.bids_header.pop('FlipAngle')
        med_volume_out.bids_header['PulseSequenceType'] = 'Multi-echo Spin Echo'

        return med_volume_out

