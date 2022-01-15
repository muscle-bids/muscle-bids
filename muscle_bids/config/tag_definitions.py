from bidict import bidict


def list_to_item(x):
    return x[0]


def item_to_list(x):
    return [x]


patient_tags = bidict({
    '00100010': 'PatientName',
    '00101001': 'OtherNames',
    '00100020': 'PatientID',
    '00100030': 'Birthdate',
    '00101010': 'Age',
    '00101040': 'PatientAddress',
    '00080080': 'InstitutionName',
    '00080081': 'InstitutionAddress',
    '00080090': 'ReferringPhysician',
    '00080094': 'ReferringPhysicianPhone',
    '00081070': 'OperatorName',
    '00101000': 'OtherPatientID',
    '00080092': 'ReferringPhysicianAddress',
    '00080050': 'AccessionNumber'
})


defined_tags = bidict({
    '00180081': 'EchoTime'
})


# some tags are defined as lists even if they are numerical. Or we might want different
# modifications before storing them into bids
tag_translators = {
    '00180081': list_to_item,
    'EchoTime': item_to_list,
}
