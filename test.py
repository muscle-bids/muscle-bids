#!/usr/bin/env python3
from muscle_bids.dosma_io import MedicalVolume
from muscle_bids.utils.headers import copy_headers
from muscle_bids.utils.io import load_dicom, save_bids, load_bids, save_dicom

INPUT_FOLDER = 'dicom_test'
OUTPUT = 'nifti_test_out/test.nii.gz'
OUTPUT_FOLDER_DICOM = 'dicom_test_out'
OUTPUT_FOLDER_DICOM_2 = 'dicom_test_out_noecho'

med_volume = load_dicom(INPUT_FOLDER, 'EchoTime')
print(med_volume.shape)
save_bids(OUTPUT, med_volume)

med_volume_2 = load_bids(OUTPUT)
#save_dicom(OUTPUT_FOLDER_DICOM, med_volume_2)

new_vol = med_volume_2.volume[:,:,:,0]

new_vol = MedicalVolume(new_vol, med_volume_2.affine)
copy_headers(med_volume_2, new_vol)

new_vol.bids_header['EchoTime'] = [0.0]
new_vol.bids_header['FourthDimension']
save_dicom(OUTPUT_FOLDER_DICOM_2, new_vol)
