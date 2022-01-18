import json

from ..dosma_io import DicomReader, DicomWriter, NiftiReader, NiftiWriter
from ..utils import headers


def load_dicom(path, group_by = None):
    dicom_reader = DicomReader(num_workers=0, group_by=None)
    medical_volume = dicom_reader.load(path)[0]
    new_volume = headers.dicom_volume_to_bids(medical_volume)
    if group_by is not None:
        new_volume = headers.group(new_volume, group_by)
    return new_volume


def save_dicom(path, medical_volume, new_series = True):
    new_volume = headers.bids_volume_to_dicom(medical_volume, new_series)
    #print(new_volume.headers().shape)
    dicom_writer = DicomWriter(num_workers=0)
    dicom_writer.save(new_volume, path)


def load_bids(nii_file):
    nifti_reader = NiftiReader()
    medical_volume = nifti_reader.load(nii_file)
    json_base_name = nii_file

    # remove extensions
    if json_base_name.lower().endswith('.gz'):
        json_base_name = json_base_name[:-3]
    if json_base_name.lower().endswith('.nii'):
        json_base_name = json_base_name[:-4]

    try:
        with open(json_base_name + '.json', 'r') as f:
            bids_header = json.load(f)
    except FileNotFoundError:
        bids_header = {}

    try:
        with open(json_base_name + '_patient.json', 'r') as f:
            patient_header = json.load(f)
    except FileNotFoundError:
        patient_header = {}

    try:
        with open(json_base_name + '_extra.json', 'r') as f:
            extra_and_meta_header = json.load(f)
    except FileNotFoundError:
        extra_and_meta_header = {'extra': {}, 'meta': {}}

    setattr(medical_volume, 'meta_header', extra_and_meta_header['meta'])
    setattr(medical_volume, 'bids_header', bids_header)
    setattr(medical_volume, 'patient_header', patient_header)
    setattr(medical_volume, 'extra_header', extra_and_meta_header['extra'])

    return medical_volume


def save_bids(nii_file, medical_volume):
    nifti_writer = NiftiWriter()
    nifti_writer.save(medical_volume, nii_file)
    json_base_name = nii_file

    # remove extensions
    if json_base_name.lower().endswith('.gz'):
        json_base_name = json_base_name[:-3]
    if json_base_name.lower().endswith('.nii'):
        json_base_name = json_base_name[:-4]

    extra_and_meta_header = {}

    extra_and_meta_header['meta'] = getattr(medical_volume, 'meta_header', {})
    extra_and_meta_header['extra'] = getattr(medical_volume, 'extra_header', {})
    bids_header = getattr(medical_volume, 'bids_header', {})
    patient_header = getattr(medical_volume, 'patient_header', {})

    with open(json_base_name + '.json', 'w') as f:
        json.dump(bids_header, f, indent=2)

    with open(json_base_name + '_patient.json', 'w') as f:
        json.dump(patient_header, f, indent=2)

    with open(json_base_name + '_extra.json', 'w') as f:
        json.dump(extra_and_meta_header, f, indent=2)



