import xarray as xr
import pygrib

# Replace 'file_path' with the path to your GRIB2 file
file_path = r'C:\Users\eraslan\Atmospheric Module\Application\gfs_files\gfs.t00z.pgrb2.0p25.f010'

# Open the GRIB2 file using xarray with the cfgrib engine
ds = xr.open_dataset(file_path)

# Now you can work with the dataset
print(ds)


