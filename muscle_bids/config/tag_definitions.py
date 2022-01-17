from collections.abc import Iterable

from bidict import bidict


def list_to_item(x):
    return x[0]


def item_to_list(x):
    return [x]


class TagDefinitionDict(dict):
    def __init__(self, d=None):
        dict.__init__(self)
        self.inverse = {}
        self.translator_dict = {}

        if d:
            for k, v in d.items():
                self.add_element(k, v)

    @staticmethod
    def __add_item(dictionary, source_tag, dest_tag):
        if isinstance(source_tag, (list, tuple)):
            for tag in source_tag:
                if isinstance(dest_tag, (list, tuple)):
                    dictionary[tag] = dest_tag[0]
                else:
                    dictionary[tag] = dest_tag
            else:
                if isinstance(dest_tag, (list, tuple)):
                    dictionary[source_tag] = dest_tag[0]
                else:
                    dictionary[source_tag] = dest_tag
        else:
            if isinstance(dest_tag, (list, tuple)):
                dictionary[source_tag] = dest_tag[0]
            else:
                dictionary[source_tag] = dest_tag

    def add_element(self, numerical_tag, named_tag, numerical_to_named_translator=None,
                    named_to_numerical_translator=None):

        self.__add_item(self, numerical_tag, named_tag)
        self.__add_item(self.inverse, named_tag, numerical_tag)

        if numerical_to_named_translator is None:
            def numerical_to_named_translator(x): return x

        if named_to_numerical_translator is None:
            def named_to_numerical_translator(x): return x

        self.__add_item(self.translator_dict, numerical_tag, numerical_to_named_translator)
        self.__add_item(self.translator_dict, named_tag, named_to_numerical_translator)

    def set_translator(self, tag, translator):
        if translator is None:
            def translator(x): return x

        self.__add_item(self.translator_dict, tag, translator)

    def get_translator(self, tag):
        return self.translator_dict[tag]


patient_tags = TagDefinitionDict({
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

defined_tags = TagDefinitionDict()

defined_tags.add_element('00180081', 'EchoTime', list_to_item, item_to_list)
defined_tags.add_element('00181314', ('FlipAngle', 'RefocusingFlipAngle'), list_to_item, item_to_list)

