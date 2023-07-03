"""
    All utility functions for generating RESQML data from FMU
"""

from zipfile import ZipFile
from io import BytesIO

from fmu.sumo.explorer import Explorer



def convert_objects_to_resqml(uuids : list[str], sumo : Explorer) -> tuple(BytesIO, BytesIO):
    """
        Converts given objects to RESQML format.

        Returns two different zip files, first containing EPC files, second HDF files.
    """
    pass


def convert_object_to_resqml(uuid : str, sumo : Explorer) -> tuple(BytesIO, BytesIO):
    """
        Converts a single object to RESQML format.

        Returns two different bytestreams, first containing an EPC, second a HDF.
    """
    pass