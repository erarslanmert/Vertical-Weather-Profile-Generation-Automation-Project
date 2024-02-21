import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
import pytz
import pandas as pd

def create_metcm_message(gfs_file, latitude, longitude):
    # Open the GFS file using xarray with cfgrib engine
    dsm = xr.open_mfdataset(paths=gfs_file, engine='cfgrib', combine='nested', concat_dim=['valid_time'], parallel=True, chunks={'time': 1},
                            backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa'}, 'errors': 'ignore'})

    # Interpolate data to obtain values at the specified location
    dprofile = dsm.interp(latitude=latitude, longitude=longitude)

    # Extract necessary variables
    temp = dprofile['t']
    rh = dprofile['r']
    u = dprofile['u']
    v = dprofile['v']
    p = dprofile['isobaricInhPa']

    # Calculate additional variables
    wind_speed = mpcalc.wind_speed(u, v)
    wind_dir = mpcalc.wind_direction(u, v, convention='from')
    mix_ratio = mpcalc.mixing_ratio_from_relative_humidity(p, temp, rh)
    virt_temp = mpcalc.virtual_temperature(temp, mix_ratio)
    dew_point = mpcalc.dewpoint_from_relative_humidity(temp, rh)
    density = mpcalc.density(p, temp, mix_ratio)

    # Convert to desired units
    temp_degC = temp.metpy.convert_units('degC').values
    rh_percent = rh.values
    wind_speed_knots = wind_speed.metpy.convert_units('knots').values
    wind_dir_degrees = wind_dir.metpy.convert_units('degrees').values
    virt_temp_degC = virt_temp.metpy.convert_units('degC').values
    dew_point_degC = dew_point.metpy.convert_units('degC').values
    density_kgm3 = density.metpy.convert_units('kg/m^3').values

    # Format METCM message
    metcm_message = f"METCM0 Latitude: {latitude}, Longitude: {longitude}\n"
    metcm_message += "Time: " + pd.to_datetime(dprofile['time'].values).strftime('%Y-%m-%d %H:%M:%S %Z') + "\n"
    metcm_message += f"Temperature (degC): {temp_degC}\n"
    metcm_message += f"Relative Humidity (%): {rh_percent}\n"
    metcm_message += f"Wind Speed (knots): {wind_speed_knots}\n"
    metcm_message += f"Wind Direction (degrees): {wind_dir_degrees}\n"
    metcm_message += f"Virtual Temperature (degC): {virt_temp_degC}\n"
    metcm_message += f"Dew Point (degC): {dew_point_degC}\n"
    metcm_message += f"Density (kg/m^3): {density_kgm3}\n"

    return metcm_message

# Example usage:
gfs_file = 'path/to/gfs_file.grib2'
latitude = 40.0
longitude = -105.0
message = create_metcm_message(gfs_file, latitude, longitude)
print(message)
