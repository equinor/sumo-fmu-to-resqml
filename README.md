# fmu-to-resqml

This is a service interacting with [fmu-sumo](https://github.com/equinor/fmu-sumo) and [resqpy](https://github.com/bp/resqpy) to convert data from FMU (Fast Model Update™) to RESQML format.

------------------------------------------------------------------

## API

### Requests:

* GET - Converting and retrieving one object 
* POST - Converting and retrieving several objects


### Endpoints:

* `url/objects/` - Converting and retrieving both EPC and HDF5 files zipped.
* `url/objects/epc` - Converting and retrieving only EPC files. Will be zipped if using POST.
* `url/objects/hdf` - Converting and retrieving only HDF5 files. Will be zipped if using POST.s

### Parameters:

Using GET - Add object uuid as parameter in request arguments using `url/.../?uuid=<object_uuid>`.

Using POST - Add object uuids as parameters in request body using format `{ uuids : <object_1_uuid>;<object_2_uuid>;<object_3_uuid>}`. 