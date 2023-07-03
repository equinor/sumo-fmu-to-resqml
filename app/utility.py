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

    # Open two Bytestreams, one for each filetype
    epcstream, hdfstream = BytesIO(), BytesIO()

    # Open said Bytestreams as ZipFiles
    with ZipFile(epcstream, "w") as epcf, ZipFile(hdfstream, "w") as hdff:
        
        # Iterate over all given uuids
        for uuid in uuids:
            # Convert current object to RESQML
            epc, hdf = convert_object_to_resqml(uuid, sumo)

            # Insert both those files (bytestreams) into each respective zipstream
            epcf.write(f"{uuid}.epc", epc.getvalue())
            hdff.write(f"{uuid}.h5", hdf.getvalue())

    # Return both zipstreams
    return epcstream, hdfstream


def convert_object_to_resqml(uuid : str, sumo : Explorer) -> tuple(BytesIO, BytesIO):
    """
        Converts a single object to RESQML format.

        Returns two different bytestreams, first containing an EPC, second a HDF.
    """
    pass