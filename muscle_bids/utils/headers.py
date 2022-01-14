import copy
from collections import OrderedDict

import numpy as np
import pydicom.dataset
from pydicom.uid import generate_uid

from ..config.tag_definitions import defined_tags, patient_tags
from ..dosma_io.med_volume import MedicalVolume


def _get_value_tag(element):
    value_tag = 'Value'
    if 'InlineBinary' in element: value_tag = 'InlineBinary'
    if 'BulkDataURI' in element: value_tag = 'BulkDataURI'
    return value_tag


def _copy_headers(medical_volume_src, medical_volume_dest):
    for header in ['bids_header', 'meta_header', 'patient_header', 'extra_header']:
        setattr(medical_volume_dest, header, copy.deepcopy(getattr(medical_volume_src, header, None)))


def headers_to_dicts(header_list):
    if type(header_list) != list:
        header_list = header_list.squeeze().tolist()

    json_header_list = []
    for h in header_list:
        meta_header = h.file_meta.to_json_dict()
        meta_header['is_little_endian'] = h.is_little_endian
        meta_header['is_implicit_VR'] = h.is_implicit_VR
        json_header_list.append({'meta': meta_header, 'header': h.to_json_dict()})

    # compress json header list
    compressed_meta = {}
    compressed_header = {}

    def process_tag(tag, content, index, dest_dictionary):
        if tag == '7FE00010': # remove pixel data
            vr_type = content['vr']
            dest_dictionary[tag] = {'vr': vr_type, 'InlineBinary': ''}
            return
        if tag not in dest_dictionary:
            dest_dictionary[tag] = content
            return
        existing_content = dest_dictionary[tag]
        if content == existing_content: return  # do nothing if the content is the same as the other slices
        # append to existing content
        # print(existing_content)

        value_tag = _get_value_tag(existing_content)

        if 'isList' not in existing_content:  # content is already a list
            existing_content['isList'] = True
            existing_content[value_tag] = [existing_content[value_tag]] * (index - 1)  # replicate content until now

        existing_content[value_tag].append(content[value_tag])

    for i, element in enumerate(json_header_list):
        for tag, content in element['header'].items():
            process_tag(tag, content, i, compressed_header)
        for tag, content in element['meta'].items():
            process_tag(tag, content, i, compressed_meta)

    return compressed_meta, compressed_header


def dicts_to_headers(n_slices, compressed_header, compressed_meta = None):
    # decompress the headers

    dicom_dataset_list = []

    header_dict_list = []
    meta_dict_list = []

    # decompress header
    for i in range(n_slices):
        new_dict = {}
        for key, element in compressed_header.items():
            new_dict[key] = copy.deepcopy(element)
            if 'isList' in element:
                value_tag = _get_value_tag(element)
                new_dict[key][value_tag] = element[value_tag][i]
                new_dict[key].pop('isList')

        vr_std = 'OW'
        try:
            vr_std = new_dict['7FE00010']['vr']
        except:
            pass
        new_dict['7FE00010'] = {'vr': vr_std, 'InlineBinary': ''} # ensure empty pixel data
        new_header = pydicom.dataset.Dataset.from_json(new_dict)
        # ensure file meta
        if compressed_meta is not None:
            is_little_endian = True
            is_implicit_VR = False
            for key, element in compressed_header.items():
                if key == 'is_little_endian':
                    if type(element) == list:
                        is_little_endian = element[i]
                    else:
                        is_little_endian = element
                    continue
                if key == 'is_implicit_VR':
                    if type(element) == list:
                        is_implicit_VR = element[i]
                    else:
                        is_implicit_VR = element
                    continue
                new_dict[key] = copy.deepcopy(element)
                if 'isList' in element:
                    value_tag = _get_value_tag(element)
                    new_dict[key][value_tag] = element[value_tag][i]
                    new_dict[key].pop('isList')
            new_meta = pydicom.dataset.FileMetaDataset.from_json(new_dict)
            new_header.file_meta = new_meta
            new_header.is_little_endian = is_little_endian
            new_header.is_implicit_VR = is_implicit_VR
            new_header.ensure_file_meta()
        else:
            new_meta = pydicom.dataset.FileMetaDataset()
            new_header.is_little_endian = True
            new_header.is_implicit_VR = False
            new_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
            new_header.file_meta = new_meta

        dicom_dataset_list.append(new_header)
        return dicom_dataset_list

def separate_headers(raw_header_dict):
    """
    this function separates the header into three dictionaries:
    the header with data useful for processing, the patient data, and the rest, which is needed for DICOM
    """

    def process_dict(output_dict, tag_dict):
        for numerical_key, named_key in tag_dict.items():
            try:
                original_content = raw_header_dict(numerical_key)
            except KeyError:
                continue
            value_tag = _get_value_tag(original_content)
            output_dict[named_key] = original_content[value_tag]
            original_content[value_tag] = ''

    patient_dict = {}
    process_dict(patient_dict, patient_tags)
    bids_dict = {}
    process_dict(bids_dict, defined_tags)
    return bids_dict, patient_dict, raw_header_dict


def remerge_headers(bids_dict, patient_dict, raw_header_dict):
    def process_dict(input_dict, tag_dict):
        for named_key, value in input_dict:
            try:
                numerical_key = tag_dict.inverse[named_key]
            except KeyError:
                print("Warning: unknown tag", named_key)
                continue
            try:
                original_content = raw_header_dict(numerical_key)
            except KeyError:
                print("Warning: tag not in header", named_key)
                continue
            value_tag = _get_value_tag(original_content)
            original_content[value_tag] = value

    process_dict(bids_dict, defined_tags)
    process_dict(patient_dict, patient_tags)

    return raw_header_dict


def group(medical_volume, key):
    assert hasattr(medical_volume, 'bids_header'), 'Error grouping: medical volume must have a bids header'
    assert medical_volume.ndim == 3, 'Error grouping: medical volume must be three dimensional'
    assert key in medical_volume.bids_header, f'Error: medical volume does not have {key}'

    indices_dict = OrderedDict({})
    all_values = medical_volume.bids_header[key]
    if type(all_values) != list:
        return medical_volume  # nothing to do

    # get all indices corresponding to separate values
    for index, value in enumerate(all_values):
        if value not in indices_dict:
            indices_dict[value] = []
        indices_dict[value].append(index)

    array_stack = []
    for value, index_list in indices_dict.items():
        array_stack.append(medical_volume.volume[:, :, index_list])

    new_volume = np.stack(array_stack, 3)

    medical_volume_out = MedicalVolume(new_volume, medical_volume.affine)

    _copy_headers(medical_volume, medical_volume_out)

    medical_volume_out.bids_header['FourthDimension'] = key
    medical_volume_out.bids_header[key] = list(indices_dict.keys())  # only keep the different values

    return medical_volume_out


def ungroup(medical_volume):
    assert hasattr(medical_volume, 'bids_header'), 'Error grouping: medical volume must have a bids header'
    assert medical_volume.ndim == 4, 'Error grouping: medical volume must be four dimensional'
    assert 'FourthDimension' in medical_volume.bids_header, f'Error: medical volume does not have a FourthDimension key'

    n_slices = medical_volume.shape[2]
    new_shape = (medical_volume.shape[0], medical_volume.shape[1], medical_volume.shape[2]*medical_volume.shape[3])
    new_volume = np.reshape(medical_volume.volume, new_shape)

    medical_volume_out = MedicalVolume(new_volume, medical_volume.affine)

    _copy_headers(medical_volume, medical_volume_out)

    fourth_dimension_key = medical_volume.bids_header['FourthDimension']
    fourth_dimension_value = medical_volume.bids_header[fourth_dimension_key]
    new_fourth_dimension_value = []

    # add a value for each slice in the header to flatten it
    for value in fourth_dimension_value:
        new_fourth_dimension_value.extend([value]*n_slices)

    medical_volume_out.bids_header.pop('FourthDimension')
    medical_volume_out.bids_header[fourth_dimension_key] = new_fourth_dimension_value

    return medical_volume_out


def dicom_volume_to_bids(medical_volume):
    compressed_meta_header, compressed_header = headers_to_dicts(medical_volume.headers())
    bids_dict, patient_dict, raw_header_dict = separate_headers(compressed_header)
    setattr(medical_volume, 'meta_header', compressed_meta_header)
    setattr(medical_volume, 'bids_header', bids_dict)
    setattr(medical_volume, 'patient_header', patient_dict)
    setattr(medical_volume, 'extra_header', raw_header_dict)
    return medical_volume

def bids_volume_to_dicom(medical_volume, new_series=False):
    if medical_volume.ndim > 3:
        medical_volume = ungroup(medical_volume)

    bids_header = getattr(medical_volume, 'bids_header', {})
    meta_header = getattr(medical_volume, 'meta_header', None)
    patient_header = getattr(medical_volume, 'patient_header', {})
    extra_header = getattr(medical_volume, 'extra_header', {})
    merged_header = remerge_headers(bids_header, patient_header, extra_header)
    new_header_list = dicts_to_headers(medical_volume.shape[2], merged_header, meta_header)

    new_series_uid = generate_uid()
    for header in new_header_list:
        header.SOPInstanceUID = generate_uid()
        if new_series:
            header.SeriesInstanceUID = new_series_uid

    new_volume = MedicalVolume(medical_volume.volume, medical_volume.affine, new_header_list)

    return new_volume
