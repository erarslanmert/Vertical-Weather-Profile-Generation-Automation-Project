import re
from datetime import timedelta, datetime

import pandas as pd
from numpy import array
from scipy.interpolate import interp1d

header_data = {}
table_data = {}
output_path = ""
acceptance_flag = 0
file_list = []
forecast_dates = []
forecast_times = []
index = 0

def interpolate_values(input_dict, target_heights):
    # Extract the original heights and Pc values from the input dictionary
    original_heights = input_dict['HeightE']
    original_Pc = input_dict['Pc']
    original_Dir = input_dict['Dir']
    original_Speed = input_dict['Speed']
    original_Temp = input_dict['VirtT']
    original_RH = input_dict['RH']
    # Interpolate the Pc values for the target heights
    interpolated_Pc = interp1d(original_heights, original_Pc, fill_value='extrapolate')(target_heights)
    interpolated_Dir = interp1d(original_heights, original_Dir, fill_value='extrapolate')(target_heights)
    interpolated_Speed = interp1d(original_heights, original_Speed, fill_value='extrapolate')(target_heights)
    interpolated_virtT = interp1d(original_heights, original_Temp, fill_value='extrapolate')(target_heights)
    interpolated_RH = interp1d(original_heights, original_RH, fill_value='extrapolate')(target_heights)
    return [interpolated_Speed, interpolated_Dir, interpolated_virtT, interpolated_RH, interpolated_Pc]


def determine_Q(latitude, longitude):
    global RPLat, RPLon
    if latitude >= 0:
        if 0 <= longitude < 90:
            Q = 0  # Northern Hemisphere, 0 to 90° W
        elif 90 <= longitude < 180:
            RPLon = longitude - 90
            Q = 1  # Northern Hemisphere, 90° to 180° W
        elif -90 <= longitude < 0:
            Q = 3  # Northern Hemisphere, 90° to 0° E
        else:
            RPLon = longitude + 90
            Q = 2  # Northern Hemisphere, 180° to 90° E
    else:
        if 0 <= longitude < 90:
            Q = 5  # Southern Hemisphere, 0° to 90° W
        elif 90 <= longitude < 180:
            RPLon = longitude - 90
            Q = 6  # Southern Hemisphere, 90° to 180° W
        elif -90 <= longitude < 0:
            Q = 8  # Southern Hemisphere, 90° to 0° E
        else:
            RPLon = longitude + 90
            Q = 7  # Southern Hemisphere, 180° to 90° E
    return Q

def format_float_to_3_digits(float_input):
    # Extract the integer part and the decimal part
    if float_input < 0:
        float_input = - float_input
    tenths = int(float_input * 10)
    # Format the output string with leading zeros if necessary
    return f"{tenths:03d}"


def calculate_forecast_date(date_list, time_list):
    result = []
    for i in range(len(date_list)):
        date_str = date_list[i][0]
        time_str = time_list[i][0]
        file_path = file_list[i]

        # Combine date and time strings into a datetime object
        date_time_str = f"{date_str} {time_str}"
        date_time_obj = datetime.strptime(date_time_str, "%d/%m/%y %H:%M:%S")

        # Extract forecast hour and time from the file name
        match = re.search(r'\.t(\d{2})z\.pgrb2\.0p25\.f(\d{3})', file_path)
        if match:
            forecast_time = int(match.group(1))
            forecast_hour = int(match.group(2))
        else:
            raise ValueError(f"Invalid file name format: {file_path}")

        # Create the forecast date and time
        forecast_done_time = date_time_obj - timedelta(hours=forecast_hour)

        forecast_done_time_str = forecast_done_time.strftime("%d/%m/%y %H:%M:%S")

        result.append(forecast_done_time_str)

    return result

def define_message():
    from datetime import datetime
    print(header_data)
    print(table_data)
    result_dates = calculate_forecast_date(forecast_dates, forecast_times)
    forecast = result_dates[index]
    print(result_dates)
    RPLat = header_data['RPLat'][0]
    RPLon = header_data['RPLon'][0]
    date = header_data['ReleaseDate'][0]
    time = header_data['ReleaseTime'][0]
    Q = determine_Q(RPLat, RPLon)
    group_1 = f'METTA{Q}'
    group_2 = format_float_to_3_digits(float(RPLat)) + format_float_to_3_digits(float(RPLon))
    parsed_date = datetime.strptime(date, '%d/%m/%y')
    day = f"{parsed_date.day:02d}"
    parsed_time = datetime.strptime(time, '%H:%M:%S')
    minute = parsed_time.minute
    minute_decimal = minute / 60
    fraction = int((minute_decimal - int(minute_decimal)) * 10)
    hour = parsed_time.hour
    group_3 = str(day) + f"{hour:02d}" + f"{fraction}1"
    height = int(header_data['RPHeightMSL'][0] / 10)
    pressure = int(header_data['GLPressure'][0]) % 1000
    data_frame = pd.DataFrame(table_data)
    zone_number_code = {
        (0,1): '00',
        (1, 50): '01',
        (50, 100): '02',
        (100, 200): '03',
        (200, 300): '04',
        (300, 400): '05',
        (400, 500): '06',
        (500, 600): '07',
        (600, 700): '08',
        (700, 800): '09',
        (800, 900): '10',
        (900, 1000): '11',
        (1000, 1100): '12',
        (1100, 1200): '13',
        (1200, 1300): '14',
        (1300, 1400): '15',
        (1400, 1500): '16',
        (1500, 1600): '17',
        (1600, 1700): '18',
        (1700, 1800): '19',
        (1800, 1900): '20',
        (1900, 2000): '21',
        (2000, 2100): '22',
        (2100, 2200): '23',
        (2200, 2300): '24',
        (2300, 2400): '25',
        (2400, 2500): '26',
        (2500, 2600): '27'
    }

    target_heights = array([0, 25, 75, 150, 250, 350, 450, 550, 650, 750, 850, 950,
        1050, 1150, 1250, 1350, 1450, 1550, 1650, 1750, 1850, 1950,
        2050, 2150, 2250, 2350, 2450, 2550])

    group_5 = []
    group_5_1 = []
    group_5_2 = []
    group_6 = []
    group_6_1 = []
    group_6_2 = []
    group_6_3 = []
    group_7 = []
    group_7_1 = []
    group_7_2 = []

    if height < 0:
        altitude = target_heights
    else:
        altitude = target_heights + table_data['HeightMSL'][0]

    interpolated_dictionary = interpolate_values(table_data, altitude)
    for alt in altitude:
        for (start, end), output in zone_number_code.items():
            if start <= (alt - altitude[0]) < end:
                group_6_1.append(output)


    for i in range(len(group_6_1)):
        direction = interpolated_dictionary[1][i] * 6400/360
        group_6_2.append(direction)
        group_6_3.append(interpolated_dictionary[0][i]*1.94384)
        text_6 = f"{group_6_1[i]}{int(group_6_2[i]) // 10 % 1000:03d}{int(group_6_3[i]):03d}"
        group_6.append(text_6)
        group_7_1.append(interpolated_dictionary[2][i]*10)
        group_7_2.append(interpolated_dictionary[3][i])
        text_7 = f"{int(group_7_1[i]):04d}{int(group_7_2[i]):02d}"
        group_7.append(text_7)

    date_stamp = date.split('/')
    temp_forcast = forecast.split(' ')
    temp_dateforecast = temp_forcast[0].split('/')
    temp_timeforecast = temp_forcast[-1].split(':')
    if int(interpolated_dictionary[-1][0]) >= 1000:
        formatted_string = f"{int(interpolated_dictionary[-1][0]):03d}"
        group_4 = f"{int(altitude[0]):03d}" + formatted_string[-3:]
    else:
        group_4 = f"{int(altitude[0]):03d}" + f"{int(interpolated_dictionary[-1][0]):03d}"
    message_header = (str(group_1) + ' ' + str(group_2) + ' ' + str(group_3) + ' ' + str(group_4) +
                      ' ' + date_stamp[1] + date_stamp[2] + ' ' + temp_timeforecast[0] + temp_dateforecast[0] + temp_dateforecast[1] + temp_dateforecast[-1])
    message_body_lines = []

    for i in range(len(group_6)):
        message_body_lines.append(f"{group_6[i]} {group_7[i]}")
    return message_header, message_body_lines


def create_message(input_header, input_table, output_directory):
    global header_data, table_data, output_path
    if acceptance_flag == 0:
        try:
            header_data = input_header
            table_data = input_table
            head, body = define_message()
            with open(output_directory, "w") as f:
                print(head, file=f)
                for part in body:
                    print(part, file=f)
        except FileNotFoundError:
            pass
    else:
        acceptance_flag == 0
        pass


