#!/usr/bin/env python3

from muscle_bids.utils.io import load_dicom, save_bids, load_bids, save_dicom

INPUT_FOLDER = 'dicom_test'
OUTPUT = 'nifti_test_out/test.nii.gz'
OUTPUT_FOLDER_DICOM = 'dicom_test_out'

med_volume = load_dicom(INPUT_FOLDER, 'EchoTime')
print(med_volume.shape)
save_bids(OUTPUT, med_volume)

med_volume_2 = load_bids(OUTPUT)
save_dicom(OUTPUT_FOLDER_DICOM, med_volume_2)