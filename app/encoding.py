""" Includes all encoder functionality. I.e. fmu -> resqml """

# Imports
import os
from zipfile import ZipFile
from io import StringIO, BytesIO

import pandas as pd
import numpy as np
import h5py

import xtgeo

from json2xml import json2xml

from fmu.sumo.explorer.objects.case import Case



def json_to_resqml(json_dict : dict) -> str:
     """
        Convert json dictionary to resqml string.
     """

     # Convert json data to xml format
     xml_data = json2xml.Json2xml(json_dict, wrapper="root").to_xml()

     return xml_data



def resqml_to_file(resqml : str, path : str) -> None:
     """
        Write resqml data to file. Overwrites existing "`path`" files.
     """
     # Open new file
     with open(path, "w") as f:
          f.writelines(resqml)


def resqml_to_stream(resqml : str) -> StringIO:
     """
          Write resqml data to string stream.
     """
     # Open and write to string stream
     stream = StringIO()
     stream.writelines(resqml)

     return stream


def write_properties_to_zip_file(properties, zipfile, object_type = "unk") -> None:
     """
          Write all property metadata to existing zipfile.
     """

     for i, property in enumerate(properties):
          # Add metadata not stored in property.metadata
          property_metadata = {}
          property_metadata["_id"] = property.uuid
          property_metadata["_source"] = property.metadata
          property_metadata["object_type"] = object_type

          # Write to file
          write_dict_to_zip_file(property_metadata, zipfile, temp_path = f"{object_type}{i}.resqml")



def write_dict_to_zip_file(dict : dict, zipfile : ZipFile, temp_path = "temp.resqml") -> None:
     """
          Write a given dictionary to zip file.
     """
     # Get the resqml data
     resqml_data = json_to_resqml(dict)

     # Write it to a temporary file
     resqml_to_file(resqml_data, temp_path)

     # Zip that temporary file data into .epc file
     zipfile.write(temp_path)

     #Remove temporary .resqml file
     os.remove(temp_path)


def write_dict_to_zip_stream(dict : dict, zipfile : ZipFile, temp_path = "temp.resqml") -> None:
     """
          Write a given dictionary to a existing zip. Only uses streams.
     """
     # Get the resqml data
     resqml_data = json_to_resqml(dict)

     # Write it to stream
     output = resqml_to_stream(resqml_data)

     # Write to zip stream
     zipfile.writestr(temp_path, output.getvalue())



def case_to_epc_file(case : Case, filename : str) -> None:
     """
      Write case metadata to "`filename`.epc" file.
     """

     # Create dirs if filename specifies it
     os.makedirs(os.path.dirname(filename), exist_ok=True)

     # Open new .epc file (zipping .resqml files together)
     with ZipFile(filename + ".epc", "w") as zip:
          # Write case metadata to zip file
          case_metadata = {}
          case_metadata["_id"] = case.uuid
          case_metadata["_source"] = case.metadata
          write_dict_to_zip_file(case_metadata, zip, temp_path = "case.resqml")


          # Write all properties to zip file
          write_properties_to_zip_file(case.cubes, zip, object_type="cube")
          write_properties_to_zip_file(case.polygons, zip, object_type="polygon")
          write_properties_to_zip_file(case.surfaces, zip, object_type="surface")
          write_properties_to_zip_file(case.tables, zip, object_type="table")


def blobs_to_hdf5(blobs : list[BytesIO], object_types : list[str]) -> bytes:
     """
          Converts blob file to hdf5.
     """
     # Open new Byte stream
     stream = BytesIO()

     # Iterate all input
     for blob, object_type in zip(blobs, object_types):

          # Convert blob to numpy array (through necessary means)
          if object_type == "surface":
               surface = xtgeo.surface_from_file(blob)
               # Save the xtgeo surface to hdf5 and output to stream
               surface.to_hdf(stream)
          else:
               df = pd.read_csv(blob, sep=",")
               column_names = df.columns
               column_values = df.transpose().values

               # Open as new hdf5 file (in the stream)
               with h5py.File(stream, "w") as f:
                    for name, column in zip(column_names, column_values):
                         f.create_dataset(f"{object_type}/{name}", data = list(column)) # Cast to list to better infer types
          
     # DEMO:
     with h5py.File(stream, "r") as f:
          print("Output:")
          for key in f.keys():
               print(key + ":", f[key])

     return stream.getvalue()
