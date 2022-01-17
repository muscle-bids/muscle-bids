from abc import ABC, abstractmethod
from ..dosma_io import MedicalVolume


class Converter(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def get_name():
        return 'Abstract converter'

    @staticmethod
    @abstractmethod
    def get_directory():
        pass

    @staticmethod
    @abstractmethod
    def get_file_name(subject_id: str):
        pass

    @staticmethod
    @abstractmethod
    def is_dataset_compatible(med_volume: MedicalVolume):
        pass

    @staticmethod
    @abstractmethod
    def convert_dataset(med_volume: MedicalVolume):
        pass
