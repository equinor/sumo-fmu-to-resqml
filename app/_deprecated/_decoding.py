""" Includes all decoder functionality. I.e. resqml -> fmu """

# Imports
import os
from zipfile import ZipFile

from functionality import deprecated

import xmltodict

from sumo.wrapper import SumoClient
from fmu.sumo.explorer.objects.case import Case
from fmu.sumo.explorer.objects.cube import Cube
from fmu.sumo.explorer.objects.polygons import Polygons
from fmu.sumo.explorer.objects.surface import Surface
from fmu.sumo.explorer.objects.table import Table


@deprecated
def read_epc_to_case(filename : str) -> Case:
    """ 
        Reads a given epc file "`filename`.epc" back into a case. 
    """

    # Temporary directory name
    temp_dir = "temp"
    
    # Extract given epc file into temporary directory
    with ZipFile(filename + ".epc", "r") as zip:
        zip.extractall(path = temp_dir)
    temp_files = os.listdir(temp_dir)

    # Case metadata is always the first within the temporary directory
    case_json = read_xml_to_json(temp_dir + "/" + temp_files[0])
    sumo_client = SumoClient(env="dev", interactive=True)
    case = Case(sumo_client, case_json)
    os.remove(temp_dir + "/" + temp_files[0])

    # Cannot directly append to CubeCollection, PolygonsCollection etc., 
    # so create new lists containing each object metadata
    case.cubes_list, case.polygons_list, case.surfaces_list, case.tables_list = [], [], [], []

    # Read the rest within the temporary directory
    for filename in temp_files[1:]:
        relative_path = temp_dir + "/" + filename
        object_metadata = read_xml_to_json(relative_path)
        # Store current object under the correct case variable given its object type
        match object_metadata["object_type"]:
            case "cube":
                case.cubes_list.append(Cube(sumo_client, object_metadata))
            case "polygon":
                case.polygons_list.append(Polygons(sumo_client, object_metadata))
            case "surface":
                case.surfaces_list.append(Surface(sumo_client, object_metadata))
            case "table":
                case.tables_list.append(Table(sumo_client, object_metadata))
            case _:
                raise Exception(f"Unknown object_type {object_metadata['object_type']}")

        # Delete the file after using it
        os.remove(relative_path)

    # Remove the empty temporary directory
    os.rmdir(temp_dir)

    return case


@deprecated
def read_xml_to_json(path : str) -> dict:
    """
        Read a given "`path`" resqml or xml file to json dict.
    """

    with open(path, "r") as f:
        # Translate directly from xml to json dict
        json_dict = xmltodict.parse(f.read())["root"]

        return prettify_xml_json_dict(json_dict)


@deprecated
def prettify_xml_json_dict(json_dict : dict) -> dict:
    """
        Json dicts translated from xml format come with extra "redundant" information like attribute-typing etc. 
        This function applies and removes these from the dictionary.

        Currently only supports following types: "bool", "str", "int", "float", "list", "dict".
    """
    pretty_dict = {}

    for key in json_dict.keys():
        child_dict = json_dict[key]
        pretty_dict[key] = _prettify_helper(child_dict)
    return pretty_dict
        

@deprecated
def _prettify_helper(child_dict : dict) -> any:
    match child_dict["@type"]:
        case "bool":
            return child_dict["#text"] == "true" # True if child_dict["#text"] stores the value true, false otherwise
        case "str":
            # If value (#text) for some reason is missing, return empty string
            if "#text" not in child_dict:
                return ""
            return child_dict["#text"]
        case "int":
            return int(child_dict["#text"])
        case "float":
            return float(child_dict["#text"])
        case "list":
            # If the list contains more than 1 item
            if type(child_dict["item"]) == list:
                pretty_list = []
                for list_item in child_dict["item"]:
                    pretty_list.append(_prettify_helper(list_item))
                return pretty_list

            # Else if the list only contains 1 item
            else:
                return [_prettify_helper(child_dict["item"])]
        case "dict":
            child_dict.pop("@type")
            pretty_dict = {}
            for key in child_dict.keys():
                pretty_dict[key] = _prettify_helper(child_dict[key])

            return pretty_dict
        case _:
            raise Exception(f"Datatype {child_dict['@type']} not yet implemented in prettify switch statement")