import os

from .abstract_converter import Converter
from ..dosma_io import MedicalVolume
from ..utils.headers import get_raw_tag_value, group


class MeGreConverter(Converter):

    @classmethod
    def get_name(cls):
        return 'MEGRE'

    @classmethod
    def get_directory(cls):
        return 'anat'

    @classmethod
    def get_file_name(cls, subject_id: str):
        return os.path.join(f'{subject_id}_megre')

    @classmethod
    def is_dataset_compatible(cls, med_volume: MedicalVolume):
        scanning_sequence = get_raw_tag_value(med_volume, '00180020')[0]
        print(scanning_sequence)
        echo_train_length = get_raw_tag_value(med_volume, '00180091')[0]
        echo_times = get_raw_tag_value(med_volume, '00180081')

        # DCam - Echo train length only used for Siemens MEGRE?
        if scanning_sequence == 'GR': # and (echo_train_length > 1 or len(echo_times) > 1):
            return True

        return False

    @classmethod
    def convert_dataset(cls, med_volume: MedicalVolume):
        med_volume_out = group(med_volume, 'EchoTime')

        # manufacturer = get_raw_tag_value(med_volume, 'Manufacturer')[0]

        med_volume_out.bids_header['PulseSequenceType'] = 'Multi-echo Gradient Echo'

        # Manufacturer-agnostic calculation of water-fat shift in pixels
        bw_per_pix = get_raw_tag_value(med_volume, '00180095')[0]
        res_freq = get_raw_tag_value(med_volume, '00180084')[0]
        water_fat_diff_ppm = 3.35
        water_fat_shift_hz = water_fat_diff_ppm * res_freq
        water_fat_shift_px = water_fat_shift_hz / bw_per_pix
        med_volume_out.bids_header['WaterFatShift'] = water_fat_shift_px

        return med_volume_out

