#!"C:\Python27_EPD32\python.exe"
from netCDF4 import Dataset
import numpy as NP
import sys

clobber = 1
complevel = 6
classic = 1
zlib = 1
shuffle = 1
fletcher32 = 0
unpackshort = 0
quantize = None
quiet = 0
nchunk = 1

lsd_dict=None

nc3tonc4(filename3,filename4,unpackshort=unpackshort,zlib=zlib,complevel=complevel,shuffle=shuffle,fletcher32=fletcher32,clobber=clobber,lsd_dict=lsd_dict,nchunk=nchunk,quiet=quiet,classic=classic)

def nc3tonc4(filename3,filename4,unpackshort=True,zlib=True,complevel=6,shuffle=True,fletcher32=False,clobber=False,lsd_dict=None,nchunk=10,quiet=False,classic=0):
    """convert a netcdf 3 file (filename3) to a netcdf 4 file
    The default format is 'NETCDF4', but can be set
    to NETCDF4_CLASSIC if classic=1.
    If unpackshort=True, variables stored as short
    integers with a scale and offset are unpacked to floats.
    in the netcdf 4 file.  If the lsd_dict is not None, variable names
    corresponding to the keys of the dict will be truncated to the decimal place
    specified by the values of the dict.  This improves compression by
    making it 'lossy'..
    The zlib, complevel and shuffle keywords control
    how the compression is done."""

    ncfile3 = Dataset(filename3,'r')
    if classic:
        ncfile4 = Dataset(filename4,'w',clobber=clobber,format='NETCDF4_CLASSIC')
    else:
        ncfile4 = Dataset(filename4,'w',clobber=clobber,format='NETCDF4')
    mval = 1.e30 # missing value if unpackshort=True
    # create dimensions. Check for unlimited dim.
    unlimdimname = False
    unlimdim = None
    # create global attributes.
    if not quiet: sys.stdout.write('copying global attributes ..\n')
    #for attname in ncfile3.ncattrs():
    #    setattr(ncfile4,attname,getattr(ncfile3,attname))
    ncfile4.setncatts(ncfile3.__dict__) 
    if not quiet: sys.stdout.write('copying dimensions ..\n')
    for dimname,dim in ncfile3.dimensions.items():
        if dim.isunlimited():
            unlimdimname = dimname
            unlimdim = dim
            ncfile4.createDimension(dimname,None)
        else:
            ncfile4.createDimension(dimname,len(dim))
    # create variables.
#    varnamelist=['temp','u','v','zeta']
    varnamelist=['zeta']
    vars = [ncfile3.variables[i] for i in varnamelist]
    myvarlist = zip(varnamelist,vars)
#    for varname,ncvar in ncfile3.variables.items():
    for varname,ncvar in myvarlist:

        if not quiet: sys.stdout.write('copying variable %s\n' % varname)
        # quantize data?
        if lsd_dict is not None and lsd_dict.has_key(varname):
            lsd = lsd_dict[varname]
            if not quiet: sys.stdout.write('truncating to least_significant_digit = %d\n'%lsd)
        else:
            lsd = None # no quantization.
        # unpack short integers to floats?
        if unpackshort and hasattr(ncvar,'scale_factor') and hasattr(ncvar,'add_offset'):
            dounpackshort = True
            datatype = 'f4'
        else:
            dounpackshort = False
            datatype = ncvar.dtype
        # is there an unlimited dimension?
        if unlimdimname and unlimdimname in ncvar.dimensions:
            hasunlimdim = True
        else:
            hasunlimdim = False
        if dounpackshort:
            if not quiet: sys.stdout.write('unpacking short integers to floats ...\n')
            sys.stdout.write('')
        if hasattr(ncvar, '_FillValue'):
            FillValue = ncvar._FillValue
        else:
            FillValue = None 
        var = ncfile4.createVariable(varname,datatype,ncvar.dimensions, fill_value=FillValue, least_significant_digit=lsd,zlib=zlib,complevel=complevel,shuffle=shuffle,fletcher32=fletcher32)
        # fill variable attributes.
        attdict = ncvar.__dict__
        if '_FillValue' in attdict: del attdict['_FillValue']
        if dounpackshort and 'add_offset' in attdict: del attdict['add_offset']
        if dounpackshort and 'scale_factor' in attdict: del attdict['scale_factor']
        if dounpackshort and 'missing_value' in attdict: attdict['missing_value']=mval
        var.setncatts(attdict)
            #for attname in ncvar.ncattrs():
        #    if attname == '_FillValue': continue
        #    if dounpackshort and attname in ['add_offset','scale_factor']: continue
        #    if dounpackshort and attname == 'missing_value':
        #        setattr(var,attname,mval)
        #    else:
        #        setattr(var,attname,getattr(ncvar,attname))
        # fill variables with data.
        if hasunlimdim: # has an unlim dim, loop over unlim dim index.
            # range to copy
            if nchunk:
                start = 0; stop = len(unlimdim); step = nchunk
                if step < 1: step = 1
                for n in range(start, stop, step):
                    nmax = n+nchunk
                    if nmax > len(unlimdim): nmax=len(unlimdim)
                    idata = ncvar[n:nmax]
                    if dounpackshort:
                        tmpdata = (ncvar.scale_factor*idata.astype('f')+ncvar.add_offset).astype('f')
                        if hasattr(ncvar,'missing_value'):
                            tmpdata = NP.where(idata == ncvar.missing_value, mval, tmpdata)
                    else:
                        tmpdata = idata
                    var[n:nmax] = tmpdata
            else:
                idata = ncvar[:]
                if dounpackshort:
                    tmpdata = (ncvar.scale_factor*idata.astype('f')+ncvar.add_offset).astype('f')
                    if hasattr(ncvar,'missing_value'):
                        tmpdata = NP.where(idata == ncvar.missing_value, mval, tmpdata)
                else:
                    tmpdata = idata
                var[0:len(unlimdim)] = tmpdata
        else: # no unlim dim or 1-d variable, just copy all data at once.
            idata = ncvar[:]
            if dounpackshort:
                tmpdata = (ncvar.scale_factor*idata.astype('f')+ncvar.add_offset).astype('f')
                if hasattr(ncvar,'missing_value'):
                    tmpdata = NP.where(idata == ncvar.missing_value, mval, tmpdata)
            else:
                tmpdata = idata
            var[:] = tmpdata
        ncfile4.sync() # flush data to disk
    # close files.
    ncfile3.close()
    ncfile4.close()

"""
 Convert a netCDF 3 file to netCDF 4 format, optionally
 unpacking variables packed as short integers (with scale_factor and add_offset)
 to floats, and adding zlib compression (with the HDF5 shuffle filter and fletcher32 checksum).
 Data may also be quantized (truncated) to a specified precision to improve compression.

 usage: %s [-h] [-o] [--zlib=(0|1)] [--complevel=(1-9)] [--shuffle=(0|1)] [--fletcher32=(0|1)] [--unpackshort=(0|1)] [--quantize=var1=n1,var2=n2,..] netcdf3filename netcdf4filename
 -h -- Print usage message.
 -o -- Overwite destination file (default is to raise an error if output file already exists).
 --classic=(0|1) -- use NETCDF4_CLASSIC format instead of NETCDF4 (default 1)
 --zlib=(0|1) -- Activate (or disable) zlib compression (default is activate).
 --complevel=(1-9) -- Set zlib compression level (6 is default).
 --shuffle=(0|1) -- Activate (or disable) the shuffle filter (active by default).
 --fletcher32=(0|1) -- Activate (or disable) the fletcher32 checksum (not
     active by default).
 --unpackshort=(0|1) -- Unpack short integer variables to float variables
     using scale_factor and add_offset netCDF variable attributes (active by default).
 --quantize=(comma separated list of "variable name=integer" pairs) --
     Truncate the data in the specified variables to a given decimal precision.
     For example, 'speed=2, height=-2, temp=0' will cause the variable
     'speed' to be truncated to a precision of 0.01, 'height' to a precision of 100
     and 'temp' to 1. This can significantly improve compression. The default
     is not to quantize any of the variables.
 --quiet=(0|1)  -- if 1, don't print diagnostic information.
 --chunk=(integer) -- number of records along unlimited dimension to 
     write at once.  Default 10.  Ignored if there is no unlimited 
     dimension.  chunk=0 means write all the data at once.
\n""" 

# default options

