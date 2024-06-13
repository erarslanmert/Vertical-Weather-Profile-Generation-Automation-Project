from datetime import datetime, timedelta, timezone


final_url = ''
tXXz = 0
fYYY = 0
url_date = ''
main_base = 'https://nomads.ncep.noaa.gov'


def create_url(test_date_str):
    global final_url, tXXz, fYYY, url_date, main_base
    base_url = f'{main_base}/pub/data/nccf/com/gfs/prod'
    date_format = "%d/%m/%y %H:%M:%S"
    download_date = datetime.utcnow().replace(tzinfo=None)  # Convert actual_date to naive datetime

    test_date = datetime.strptime(test_date_str, date_format).replace(tzinfo=None)  # Convert test_date to naive datetime
    
    time_suffix = ''


    integer_utc = int(download_date.hour)

    # Calculate the time difference
    time_difference = test_date - download_date

    # Extract hours from the time difference
    diff = time_difference.total_seconds() / 3600

    day_step = 0
    start_time = ""
    if integer_utc >= 0 and integer_utc < 6:
        start_time = "18:00:00"
        time_suffix = '18'
        day_step = 1
    elif integer_utc >= 6 and integer_utc < 12:
        start_time = "00:00:00"
        time_suffix = '00'
        day_step = 0
    elif integer_utc >= 12 and integer_utc < 18:
        start_time = "06:00:00"
        time_suffix = '06'
        day_step = 0
    else:
        start_time = "12:00:00"
        time_suffix = '12'
        day_step = 0

    tXXz = time_suffix
    

    url_date = download_date - timedelta(days = day_step)

    calculation_date = url_date.date()

    final_date = datetime.combine(calculation_date, datetime.strptime(start_time, "%H:%M:%S").time())

    diff_fYYY = test_date - final_date

    fYYY = int(diff_fYYY.total_seconds() / 3600)
    
    url_date_part = f"{calculation_date.year}{calculation_date.month:02d}{calculation_date.day:02d}"

    final_url = f"{main_base}/pub/data/nccf/com/gfs/prod/gfs.{url_date_part}/{tXXz}/atmos/gfs.t{tXXz}z.pgrb2.0p25.f{fYYY:03d}"

    return final_url




