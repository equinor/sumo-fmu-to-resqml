# fmu-to-resqml

This is a service interacting with [fmu-sumo](https://github.com/equinor/fmu-sumo) and [resqpy](https://github.com/bp/resqpy) to convert data from FMU (Fast Model Update™) to RESQML format.

------------------------------------------------------------------

## API

### Requests:

* GET - Converting and retrieving 1 object 
* POST - Converting and retrieving several objects


### Endpoints:

* *url*/objects/ - Converting and retrieving both EPC and HDF5 files zipped.
* *url*/objects/epc - Converting and retrieving only EPC files. Will be zipped if using POST.
* *url*/objects/hdf - Converting and retrieving only HDF5 files. Will be zipped if using POST.s