import sys
from muscle_bids.utils.io import load_dicom


if __name__ == '__main__':
    dir = sys.argv[1]
    med_volume = load_dicom(dir)