#!/usr/bin/env python3
import os
import sys

from muscle_bids.dosma_io import MedicalVolume, DicomReader
from muscle_bids.utils.headers import reduce, dicom_volume_to_bids, get_raw_tag_value
from muscle_bids.utils.io import load_dicom, save_bids, load_bids, save_dicom

import muscle_bids.converters

INPUT_FOLDER = 'C:\\Users\\francesco\\Desktop\\Data\\MESE_Anon'
OUTPUT = 'C:\\Users\\francesco\\Desktop\\Data\\MESE_Nii\\test.nii.gz'
OUTPUT_FOLDER_DICOM = 'C:\\Users\\francesco\\Desktop\\Data\\dicom_test_out'
OUTPUT_FOLDER_DICOM_2 = 'C:\\Users\\francesco\\Desktop\\Data\\dicom_test_out_noecho'

TEST_ENHANCED = 'C:\\Users\\francesco\\Desktop\\Data\\Philips_MESE_T2.dcm'

r = DicomReader(num_workers=0, ignore_ext=True, group_by='SeriesInstanceUID')
im = r.load(TEST_ENHANCED)
im_bids = dicom_volume_to_bids(im[0])

v = get_raw_tag_value(im_bids, '00089208')

print(im_bids.affine)

print(v)

from muscle_bids.converters.mese_philips import MeSeConverterPhilipsMagnitude

print(MeSeConverterPhilipsMagnitude.is_dataset_compatible(im_bids))

data_out = MeSeConverterPhilipsMagnitude.convert_dataset(im_bids)
print(data_out.volume.shape)
print('.\\' + MeSeConverterPhilipsMagnitude.get_file_name('test') + '.nii.gz')
print(data_out.affine)
save_bids('.\\' + MeSeConverterPhilipsMagnitude.get_file_name('test') + '.nii.gz', data_out)

sys.exit(0)
#
print(muscle_bids.converters.MeSeConverter.find(INPUT_FOLDER))


med_volume = load_dicom(INPUT_FOLDER, 'EchoTime')
print(med_volume.shape)
save_bids(OUTPUT, med_volume)

med_volume_2 = load_bids(OUTPUT)
#save_dicom(OUTPUT_FOLDER_DICOM, med_volume_2)

new_vol = med_volume_2.volume[:,:,:,0]

new_vol = reduce(med_volume_2, 0)
save_dicom(OUTPUT_FOLDER_DICOM_2, new_vol)
