#!/usr/bin/env python3

import sys
from muscle_bids.utils.io import load_dicom, save_bids
from muscle_bids.converters import converter_list
import pathlib


if __name__ == '__main__':
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]
    med_volume = load_dicom(inputDir)

    for converter_class in converter_list:
        if converter_class.is_dataset_compatible(med_volume):
            print('Volume compatible with', converter_class.get_name())
            output_path = pathlib.Path(outputDir) / converter_class.get_directory()
            output_path.mkdir(parents=True, exist_ok=True)
            converted_volume = converter_class.convert_dataset(med_volume)
            save_bids(str(output_path / converter_class.get_file_name('test')) + '.nii.gz', converted_volume)
            print('Volume saved')
            break

