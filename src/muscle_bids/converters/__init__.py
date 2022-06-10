from .mese import MeSeConverter
from .megre import MeGreConverter
from .mese_philips import MeSeConverterPhilipsMagnitude, MeSeConverterPhilipsPhase, MeSeConverterPhilipsReconstructedMap
from .quantitative_maps import T1Converter, T2Converter, FFConverter, B0Converter, B1Converter

converter_list = [
    MeSeConverter,
    MeGreConverter,
    MeSeConverterPhilipsMagnitude,
    MeSeConverterPhilipsPhase,
    MeSeConverterPhilipsReconstructedMap
]