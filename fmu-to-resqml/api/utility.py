"""
    All utility functions for generating RESQML data from FMU
"""

import os

from zipfile import ZipFile
from io import BytesIO

import xtgeo
import numpy as np
import pandas as pd

from resqpy.model import Model
from resqpy.crs import Crs
from resqpy.surface import Mesh, PointSet
from resqpy.property import StringLookup

from fmu.sumo.explorer import Explorer
from fmu.sumo.explorer.objects import Surface, Polygons


# TODO: There currently exists an error in this function, closely related to resqpy
# Sometimes creating an ensemble works, other times not. Unclear why.
def convert_ensemble_to_resqml(uuid : str, iterations : list[str], tagnames : list[str], names : list[str], sumo : Explorer) -> tuple[BytesIO, BytesIO]:
    """
        Converts an ensemble of a given case object to RESQML format.

        Returns two different zip files, first containing EPC files, second HDF files.
    """

    # Temporary filename as resqpy cannot write directly to stream
    TEMP_FILE_NAME = "ensemble_" + str(uuid)

    # Retrieve the case by the case ID
    try:
        case = sumo.get_case_by_uuid(uuid)
    except Exception as e:
        raise Exception(e.args[0], 404)

    # Create a resqpy model
    model = Model(epc_file = TEMP_FILE_NAME + ".epc", new_epc=True, create_basics = True, create_hdf5_ext = True)

    # Also add a main CRS to the model
    main_crs = Crs(model, title="Main Coordinate Reference System")
    main_crs.create_xml()

    # As names are optional, we need a seperate check
    names = names if names != [""] else True

    # Then we can iterate and add all objects which fit the filters into the RESQML object
    crss = {}
    meshes, pointsets = [], []

    # First we do surfaces (meshes)
    surfaces = case.surfaces.filter(iteration=iterations, tagname=tagnames, name=names)
    for surface in surfaces:
        # Ensure that object is a realization
        if surface.realization == None:
            continue
        # If it is, generate and store its mesh
        meshes.append(_generate_mesh_from_surface(model, surface, crss))

    # Then we do polygons (pointsets)
    polygonss = case.polygons.filter(iteration=iterations, tagname=tagnames, name=names)
    for polygons in polygonss:
        # Ensure that object is a realization
        if polygons.realization == None:
            continue
        # If it is, generate and store its pointset
        pointsets.append(_generate_pointset_from_polygons(model, polygons, crss))

    # Then we write and store the output of the model into temporary files
    # Write to epc file
    for crs in crss.values():
        crs.create_xml()
    for mesh in meshes:
        mesh.create_xml()
    for pointset in pointsets:
        pointset.create_xml()
    model.store_epc(TEMP_FILE_NAME + ".epc")

    # Write to hdf5 file
    for mesh in meshes:
        mesh.write_hdf5()
    for pointset in pointsets:
        pointset.write_hdf5()
    model.create_hdf5_ext(file_name=TEMP_FILE_NAME + ".h5")
        
    # Open two Bytestreams, one for each filetype
    epcstream, hdfstream = BytesIO(), BytesIO()

    # Read from the temporary files into the streams
    with open(TEMP_FILE_NAME + ".epc", "rb") as epcf, open(TEMP_FILE_NAME + ".h5", "rb") as hdff:
        epcstream.write(epcf.read())
        hdfstream.write(hdff.read())

    # Remove temporary .epc and .h5 written to by resqpy
    os.remove(TEMP_FILE_NAME + ".epc")
    os.remove(TEMP_FILE_NAME + ".h5")

    # Return the two different streams
    return epcstream, hdfstream


def convert_objects_to_resqml(uuids : list[str], sumo : Explorer) -> tuple[BytesIO, BytesIO]:
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
            epcf.writestr(f"{uuid}.epc", epc.getvalue())
            if len(hdf.getvalue()) > 0: ## Only write hdf file if it actually contains any data
                hdff.writestr(f"{uuid}.h5", hdf.getvalue())

    # Return both zipstreams
    return epcstream, hdfstream


def convert_object_to_resqml(uuid : str, sumo : Explorer) -> tuple[BytesIO, BytesIO]:
    """
        Converts a single object to RESQML format.

        Returns two different bytestreams, first containing an EPC, second a HDF.
    """

    # Retrieve all metadata of the given object
    try:
        object_metadata = sumo._utils.get_object(uuid)
    except Exception as e:
        raise Exception(e.args[0], 404)

    # Isolate the object_type
    object_type = object_metadata["_source"]["class"]

    # Objects are handled differently depending on the object type
    match object_type:
        case "surface":
            return _convert_surface_to_resqml(uuid, sumo)
        case "polygons":
            return _convert_polygons_to_resqml(uuid, sumo)
        case "table":
            return _convert_table_to_resqml(uuid, sumo)
        case _:
            raise Exception(f"RESQML conversion of given object type: '{object_type}' not implemented.", 501)


def _convert_surface_to_resqml(uuid : str, sumo : Explorer) -> tuple[BytesIO, BytesIO]:
    """
        Converts a surface object to RESQML form.

        Returns two different bytestreams, first containing an EPC, second a HDF.
    """

    # Temporary filename as resqpy cannot write directly to stream
    TEMP_FILE_NAME = "surface_" + str(uuid)

    # Retrieve surface object from explorer
    try:
        surface = sumo.get_surface_by_uuid(uuid)
    except Exception as e:
        raise Exception(e.args[0], 404)
    metadata = surface.metadata
    spec = metadata['data']['spec']

    # Create Bytestreams for EPC and HDF files
    epcstream, hdfstream = BytesIO(), BytesIO()

    # Instantiate resqpy model of surface
    model = Model(epc_file=TEMP_FILE_NAME + ".epc", new_epc=True, create_basics = True, create_hdf5_ext = True)

    # Add a mandatory coordinate reference
    x_offset = spec['xori']
    y_offset = spec['yori']
    rotation = spec['rotation']
    z_inc_down = bool(spec['yflip']) # Determines "handedness" of coordinate system https://en.wikipedia.org/wiki/Right-hand_rule#Coordinates
    title = "Surface Coordinate Reference System"

    crs = Crs(model, x_offset=x_offset, y_offset=y_offset, rotation=rotation, z_inc_down=z_inc_down, title=title)

    # Add a mesh (2D grid) of the surface data
    regsurf = xtgeo.surface_from_file(surface.blob)
    regsurf.values.fill_value = spec['undef']

    origin = (0,0,0)
    ni = spec['nrow']
    nj = spec['ncol']
    dxyz_dij = np.array([[spec['xinc'], 0, 0],
                         [0, spec['yinc'], 0]])
    z_values = regsurf.values
    crs_uuid = crs.uuid
    title = "Surface Mesh"

    mesh = Mesh(model, z_values=z_values, origin=origin, ni=ni, nj=nj, dxyz_dij=dxyz_dij, crs_uuid=crs_uuid, title=title)

    # Append fmu metadata dict to the mesh
    extra_metadata = metadata
    extra_metadata['uuid'] = surface.uuid
    mesh.append_extra_metadata(extra_metadata)

    # Write out all metadata to the epc file
    crs.create_xml()
    mesh.create_xml()
    model.store_epc(TEMP_FILE_NAME + ".epc")

    # Write data to the hdf5 file
    mesh.write_hdf5()
    model.create_hdf5_ext(file_name=TEMP_FILE_NAME + ".h5")

    # Read from the temporary files into the streams
    with open(TEMP_FILE_NAME + ".epc", "rb") as epcf, open(TEMP_FILE_NAME + ".h5", "rb") as hdff:
        epcstream.write(epcf.read())
        hdfstream.write(hdff.read())

    # Remove temporary .epc and .h5 written to by resqpy
    os.remove(TEMP_FILE_NAME + ".epc")
    os.remove(TEMP_FILE_NAME + ".h5")

    # Return the bytestreams
    return epcstream, hdfstream


def _convert_polygons_to_resqml(uuid : str, sumo : Explorer) -> tuple[BytesIO, BytesIO]:
    """
        Converts a polygons object to RESQML form.

        Returns two different bytestreams, first containing an EPC, second a HDF.
    """
    
    # Temporary filename as resqpy cannot write directly to stream
    TEMP_FILE_NAME = "polygons_" + str(uuid)

    # Retrieve polygons object from explorer
    try:
        polygons = sumo.get_polygons_by_uuid(uuid)
    except Exception as e:
        raise Exception(e.args[0], 404)
    metadata = polygons.metadata
    spec = metadata['data']['spec']

    # Create Bytestreams for EPC and HDF files
    epcstream, hdfstream = BytesIO(), BytesIO()

    # Instantiate resqpy model of polygons
    model = Model(epc_file=TEMP_FILE_NAME + ".epc", new_epc=True, create_basics = True, create_hdf5_ext = True)

    # Add mandatory default coordinate reference system
    title = "Default Coordinate Reference System"
    crs = Crs(model, title=title)

    # Add a pointset of the polygons data
    df = pd.read_csv(polygons.blob)

    crs_uuid = crs.uuid
    title = "Polygons Point Set"
    pointset = PointSet(model, crs_uuid=crs_uuid, title=title)

    # Append fmu metadata dict to the pointset
    extra_metadata = metadata
    extra_metadata['uuid'] = polygons.uuid
    pointset.append_extra_metadata(extra_metadata) 

    # Add all different polygons as different patches
    id_string = 'POLY_ID' if 'POLY_ID' in df.columns else 'ID'
    for id in range(0, spec['npolys']):
        pointset.add_patch(df.loc[df[id_string] == id].to_numpy()[:, :3])

    # Write out all metadata to the epc file
    crs.create_xml()
    pointset.create_xml()
    model.store_epc(TEMP_FILE_NAME + ".epc")

    # Write data to the hdf5 file
    pointset.write_hdf5()
    model.create_hdf5_ext(file_name=TEMP_FILE_NAME + ".h5")

    # Read from the temporary files into the streams
    with open(TEMP_FILE_NAME + ".epc", "rb") as epcf, open(TEMP_FILE_NAME + ".h5", "rb") as hdff:
        epcstream.write(epcf.read())
        hdfstream.write(hdff.read())

    # Remove temporary .epc and .h5 written to by resqpy
    os.remove(TEMP_FILE_NAME + ".epc")
    os.remove(TEMP_FILE_NAME + ".h5")

    # Return the bytestreams
    return epcstream, hdfstream


def _convert_table_to_resqml(uuid : str, sumo : Explorer) -> tuple[BytesIO, BytesIO]:
    """
        Converts a table object to RESQML form.

        Returns two different bytestreams, first containing an EPC, second an empty HDF.
    """
    
    # Temporary filename as resqpy cannot write directly to stream
    TEMP_FILE_NAME = "table_" + str(uuid)

    # Retrieve table object from explorer
    try:
        table = sumo.get_table_by_uuid(uuid)
    except Exception as e:
        raise Exception(e.args[0], 404)
    metadata = table.metadata
    spec = metadata['data']['spec']

    # Create Bytestreams for EPC and HDF files (hdf will be empty)
    epcstream, hdfstream = BytesIO(), BytesIO()

    # Instantiate resqpy model of table
    model = Model(epc_file=TEMP_FILE_NAME + ".epc", new_epc=True, create_basics = True, create_hdf5_ext = False)

    # Add a string lookup table of the table data
    match metadata['data']['format']:
        case 'csv':
            df = pd.read_csv(table.blob)
        case 'arrow':
            df = pd.read_parquet(table.blob, engine="pyarrow")

    title = "String Table Lookup"
    stringlu = StringLookup(model, title=title)

    # Load table into dictionary where key is row number (as key in StringLookup has to be integer)
    tabledict = { i:row for i,row in enumerate(df.values.tolist()) }
    stringlu.load_from_dict(tabledict)

    # Append fmu metadata dict to the lookup table
    extra_metadata = metadata
    extra_metadata['uuid'] = table.uuid
    stringlu.append_extra_metadata(extra_metadata) 

    # Write out all metadata to the epc file
    ## NOTE: StringLookup doesn't write to hdf5. Thus all data has to be stored in .epc
    stringlu.create_xml()
    model.store_epc(TEMP_FILE_NAME + ".epc")

    # Read from the temporary file into the stream
    with open(TEMP_FILE_NAME + ".epc", "rb") as epcf:
        epcstream.write(epcf.read())

    # Remove temporary .epc written to by resqpy
    os.remove(TEMP_FILE_NAME + ".epc")

    # Return the bytestreams (even the empty hdf one)
    return epcstream, hdfstream


def _hash_object_spec(spec : dict) -> int:
    """
        Function used for hashing a dictionary.
    """
    return hash(frozenset(spec.items()))

def _generate_crs_from_spec(model : Model, spec : dict) -> Crs:
    """
        Generate a resqpy Coordinate Reference System contained in the given model from a 'spec' dictionary.
    """
    x_offset = spec['xori']
    y_offset = spec['yori']
    rotation = spec['rotation']
    z_inc_down = bool(spec['yflip']) # Determines "handedness" of coordinate system https://en.wikipedia.org/wiki/Right-hand_rule#Coordinates
    title = "Coordinate Reference System"

    return Crs(model, x_offset=x_offset, y_offset=y_offset, rotation=rotation, z_inc_down=z_inc_down, title=title)

def _generate_mesh_from_surface(model : Model, surface : Surface, crss : dict) -> Mesh:
    """
        Generate a resqpy mesh object contained in the given model from a surface object.
    """

    # Generate the Crs for the surface (Only if another mesh doesn't use the same crs)
    spec_hash = _hash_object_spec(surface.spec)
    if spec_hash not in crss:
        crss[spec_hash] = _generate_crs_from_spec(model, surface.spec)

    # Retrieve the surface's respective crs
    crs = crss[spec_hash]

    # Create the mesh for the object
    regsurf = xtgeo.surface_from_file(surface.blob)
    regsurf.values.fill_value = surface.spec['undef']

    # Here xy(z) -> ij where i = x, j = y dirs
    origin = (0,0,0)
    ni = surface.spec['nrow']
    nj = surface.spec['ncol']
    dxyz_dij = np.array([[surface.spec['xinc'], 0, 0],
                         [0, surface.spec['yinc'], 0]])
    z_values = regsurf.values
    crs_uuid = crs.uuid
    title = "Surface Mesh"

    mesh = Mesh(model, z_values=z_values, origin=origin, ni=ni, nj=nj, dxyz_dij=dxyz_dij, crs_uuid=crs_uuid, title=title)

    # Append fmu metadata dict to the mesh
    extra_metadata = surface.metadata
    extra_metadata['uuid'] = surface.uuid
    mesh.append_extra_metadata(extra_metadata)

    # Return the mesh
    return mesh


def _generate_pointset_from_polygons(model : Model, polygons : Polygons, crss : dict) -> PointSet:
    """
        Generate a resqpy pointset object contained in the given model from a surface object.
    """

    # Generate the Crs for the polygons (Only if another mesh doesn't use the same crs)
    spec_hash = _hash_object_spec(polygons.spec)
    if spec_hash not in crss:
        crss[spec_hash] = _generate_crs_from_spec(model, polygons.spec)

    # Retrieve the polygons' respective crs
    crs = crss[spec_hash]

    # Add a pointset of the polygons data
    df = pd.read_csv(polygons.blob)

    crs_uuid = crs.uuid
    title = "Polygons Point Set"
    pointset = PointSet(model, crs_uuid=crs_uuid, title=title)

    # Append fmu metadata dict to the pointset
    extra_metadata = polygons.metadata
    extra_metadata['uuid'] = polygons.uuid
    pointset.append_extra_metadata(extra_metadata) 

    # Add all different polygons as different patches
    id_string = 'POLY_ID' if 'POLY_ID' in df.columns else 'ID'
    for id in range(0, polygons.spec['npolys']):
        pointset.add_patch(df.loc[df[id_string] == id].to_numpy()[:, :3])

    # Return the pointset
    return pointset