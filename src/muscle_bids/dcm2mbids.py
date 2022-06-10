#!/usr/bin/env python3

import sys
from .utils.io import load_dicom, save_bids, load_dicom_with_subfolders
from .converters import converter_list
import pathlib

import argparse

def main():
    parser = argparse.ArgumentParser(description='Convert DICOM to BIDS format')
    parser.add_argument('input_folder', type=str, help='Input folder')
    parser.add_argument('output_folder', type=str, help='Output folder')
    parser.add_argument('--anonymize', '-a', const='anon', metavar='pseudo_name', dest='anonymize', type=str, nargs = '?', help='Use the pseudo_name (default: anon) as patient name')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recurse into subfolders')

    args = parser.parse_args()

    inputDir = args.input_folder
    outputDir = args.output_folder
    ANON_NAME = args.anonymize
    RECURSIVE = args.recursive

    if RECURSIVE:
        med_volume_list = load_dicom_with_subfolders(inputDir)
    else:
        med_volume_list = [load_dicom(inputDir)]

    for med_volume in med_volume_list:
        for converter_class in converter_list:
            if converter_class.is_dataset_compatible(med_volume):
                print('Volume compatible with', converter_class.get_name())
                output_path = pathlib.Path(outputDir) / converter_class.get_directory()
                output_path.mkdir(parents=True, exist_ok=True)
                converted_volume = converter_class.convert_dataset(med_volume)
                if ANON_NAME:
                    patient_name = ANON_NAME
                else:
                    patient_name = med_volume.patient_header['PatientName']
                save_bids(str(output_path / converter_class.get_file_name(patient_name)) + '.nii.gz', converted_volume)
                print('Volume saved')


