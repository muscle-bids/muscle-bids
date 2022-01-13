from ..dosma_io.med_volume import MedicalVolume
from ..dosma_io.io import DicomReader


def load_dicom(path):
    dicom_reader = DicomReader(num_workers=0)
    medical_volume = dicom_reader.load(path)
    return medical_volume[0]


