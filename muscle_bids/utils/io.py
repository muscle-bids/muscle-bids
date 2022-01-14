from ..dosma_io import DicomWriter
from ..dosma_io.io import DicomReader
from ..utils import headers


def load_dicom(path, group_by = None):
    dicom_reader = DicomReader(num_workers=0)
    medical_volume = dicom_reader.load(path)[0]
    new_volume = headers.dicom_volume_to_bids(medical_volume)
    if group_by is not None:
        new_volume = headers.group(new_volume, group_by)
    return new_volume


def save_dicom(path, medical_volume, new_series = True):
    new_volume = headers.bids_volume_to_dicom(medical_volume, new_series)
    dicom_writer = DicomWriter(num_workers=0)
    dicom_writer.save(new_volume, path)


