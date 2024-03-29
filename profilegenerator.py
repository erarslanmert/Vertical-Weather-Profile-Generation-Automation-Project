import os
from pathlib import Path
from multiprocessing.pool import Pool
from functools import partial
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
import pandas as pd
import pytz
import dashboard, create_METCM

dsm = []
input_dir = ''
output_dir = ''
input_lat = 0
input_lon = 0
input_date = ''
input_wrf_time = ''
class VirtualSoundingGenMultiGFS:

    def __init__(self):
        self.sett_MP_enabled = False
        self.sett_Npar = 2
        self.sett_g0 = 9.80665 * units('m/s^2')
        self.sett_dt_h = 0.25
        self.wrfDate = None
        self.wrfTime = None
        self.wrfTz = None
        self.wrfCenterType = None
        self.baseInputDir = None
        self.baseOutputDir = None


    def getDSInfo(self):

        gfs_file_dict = {'basefiledir_s': input_dir,
                         'baseOutput_s': output_dir,
                         'wrfDate': input_date,
                         'wrfTime': input_wrf_time,
                         'wrfTz': pytz.timezone('UTC'),
                         'wsLat': input_lat,
                         'wsLon': input_lon
                         }

        dict_DSInfo = {'file_key': gfs_file_dict
                       }

        return dict_DSInfo

    def init(self, dsInfoKey):
        global dsm
        dsInfoDict = self.getDSInfo()
        dsInfo = dsInfoDict[dsInfoKey]

        self.baseInputDir = input_dir
        self.baseOutputDir = output_dir

        self.wrfDate = dsInfo['wrfDate']
        self.wrfTime = dsInfo['wrfTime']
        self.wrfTz = dsInfo['wrfTz']
        self.wrfCenterType = 'kwbc'  # GFS
        self.wsTz = pytz.utc
        self.wsDate = self.wrfDate

        wsLat = dsInfo['wsLat']
        wsLon = dsInfo['wsLon']
        files = self.baseInputDir

        print("<II> Opening dataset")
        dsm = xr.open_mfdataset(paths=files, engine='cfgrib', combine='nested', concat_dim='valid_time', parallel=False, chunks= {'time': 1},
                                backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa'}, 'errors': 'ignore'})

        print(dsm)

        wrf_valid_times = dsm.valid_time

        if self.sett_MP_enabled:
            print(f"<II> Computing [{len(wrf_valid_times)}] times in [{self.sett_Npar}] parallel threads")
            pool = Pool(processes=self.sett_Npar)
            pool.map(partial(self.genProfile, wsLat=wsLat, wsLon=wsLon, ds=dsm), wrf_valid_times)
            pool.close()
        else:
            print(f"<II> Computing [{len(wrf_valid_times)}] times in serial")
            for wrf_time in wrf_valid_times:
                self.genProfile(wrf_time, wsLat, wsLon, dsm)

        print("<II> Done")

    def genProfile(self, wrf_time, wsLat, wsLon, ds):
        dprofile = ds.interp(valid_time=wrf_time, latitude=wsLat, longitude=wsLon)

        hght = mpcalc.geopotential_to_height(dprofile.gh.values * units.meter * self.sett_g0)
        p = dprofile.isobaricInhPa
        temp = dprofile.t.compute()

        rh = dprofile.r.compute()
        u = dprofile.u.compute()
        v = dprofile.v.compute()
        w = dprofile.w.compute()

        wind_speed = mpcalc.wind_speed(u, v)
        wind_dir = mpcalc.wind_direction(u, v, convention='from')

        mix_ratio = mpcalc.mixing_ratio_from_relative_humidity(p, temp, rh)
        virt_temp = mpcalc.virtual_temperature(temp, mix_ratio)
        dew_point = mpcalc.dewpoint_from_relative_humidity(temp, rh)
        density = mpcalc.density(p, temp, mix_ratio)

        hght_e = hght.m
        p_e = p.values
        temp_e = temp.values
        temp_degC_e = units.degC.from_(temp_e * units(temp.units)).m
        rh_e = rh.values
        virt_temp_e = virt_temp.values
        wind_speed_e = wind_speed.values
        wind_dir_e = wind_dir.values

        wsReleaseDate = pd.to_datetime(dprofile.valid_time.values, utc=True).strftime('%d/%m/%y')
        wsReleaseTime = pd.to_datetime(dprofile.valid_time.values, utc=True).strftime('%H:%M:%S')

        wsHE = hght.m[0]
        wsHMSL = hght.m[0]
        ws_P = p.values[0]
        ws_T = units.degC.from_(temp.data * units(temp.units))[0].m
        ws_RH = rh.values[0]
        ws_wind_speed = wind_speed.values[0]
        ws_wind_dir = wind_dir.values[0]


        header_data = {'SystemTrademarkAndModel': ['VirtualSounding'],
                       'SoftwareVersion': ['N/A'],
                       'NatoSoundingId': ['N/A'],
                       'ReleaseDate': [wsReleaseDate],
                       'ReleaseTime': [wsReleaseTime],
                       'RPLat': [wsLat],
                       'RPLon': [wsLon],
                       'RPHeightE': [wsHE],
                       'RPHeightMSL': [wsHMSL],
                       'GLPressure': [ws_P],
                       'GLTemp': [ws_T],
                       'GLRH': [ws_RH],
                       'GLSpeed': [ws_wind_speed],
                       'GLDir': [ws_wind_dir],
                       'SondeType': ['virtual'],
                       'SondeId': ['01'],
                       'Comments': 'GFS'}

        table_data = {'Elapsed time': 0,
                      'HeightMSL': hght_e,
                      'Pc': p_e,
                      'Pm': 9999,
                      'Temp': temp_degC_e,
                      'RH': rh_e,
                      'VirtT': virt_temp_e,
                      'Lat': wsLat,
                      'Lon': wsLon,
                      'HeightE': hght_e,
                      'Speed': wind_speed_e,
                      'Dir': wind_dir_e}

        dfh = pd.DataFrame(header_data).transpose()
        dft = pd.DataFrame(table_data)

        aux_date_str = pd.to_datetime(wrf_time.values, utc=True).astimezone(pytz.utc).strftime('%Y%m%d_%H%M%SZ')
        fileOutput = f"{self.baseOutputDir}_{aux_date_str}.csv"

        Path(os.path.dirname(fileOutput)).mkdir(parents=True, exist_ok=True)

        create_METCM.header_data = header_data
        create_METCM.table_data = table_data


        dfh.to_csv(path_or_buf=fileOutput, sep='\t', header=False)
        dft.to_csv(path_or_buf=fileOutput, sep='\t', mode='a', index_label='n')
        dashboard.df = dft
        print('Virtual Profile written: ' + os.path.basename(fileOutput))
        print(dfh)
        print(dft)



        dashboard.input_header = header_data
        dashboard.input_table = table_data


def start_reading_gfs():
    vs_gen = VirtualSoundingGenMultiGFS()
    vs_gen.init('file_key')
