import re
from datetime import timedelta, datetime
import pandas as pd

header_data = {}
table_data = {}
output_path = ""
acceptance_flag = 0
file_list = []
forecast_dates = []
forecast_times = []
index = 0


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
    group_1 = f'METAV{Q}'
    group_2 = format_float_to_3_digits(float(RPLat)) + format_float_to_3_digits(float(RPLon))
    parsed_date = datetime.strptime(date, '%d/%m/%y')
    day = f"{parsed_date.day:02d}"
    parsed_time = datetime.strptime(time, '%H:%M:%S')
    minute = parsed_time.minute
    minute_decimal = minute / 60
    fraction = int((minute_decimal - int(minute_decimal)) * 10)
    hour = parsed_time.hour
    group_3 = str(day) + f"{hour:02d}" + f"{fraction}1"

    # Get the actual height values from the data (starting from the lowest positive or 0 altitude)
    heights = table_data['HeightMSL']

    # Select the minimum height including 0 and the lowest positive value
    min_altitude = min(h for h in heights if h >= 0)

    # Filter heights to include only values below 30,000 meters
    valid_heights = [h for h in heights if h < 30000]

    group_5 = []
    group_6 = []

    for i, alt in enumerate(valid_heights):
        direction = table_data['Dir'][i] * 6400 / 360
        speed = table_data['Speed'][i] * 1.94384  # Convert to knots
        text_5 = f"{int(alt):05d}{int(direction) // 10 % 1000:03d}{int(speed):03d}"
        group_5.append(text_5)
        temp = table_data['VirtT'][i] * 10
        pressure = table_data['Pc'][i]
        text_6 = f"{int(temp):04d}{int(pressure):04d}"
        group_6.append(text_6)

    if int(table_data['Pc'][0]) >= 1000:
        formatted_string = f"{int(table_data['Pc'][0]):03d}"
        group_4 = f"{int(min_altitude):03d}" + formatted_string[-3:]
    else:
        group_4 = f"{int(min_altitude):03d}" + f"{int(table_data['Pc'][0]):03d}"

    date_stamp = date.split('/')
    temp_forcast = forecast.split(' ')
    temp_dateforecast = temp_forcast[0].split('/')
    temp_timeforecast = temp_forcast[-1].split(':')
    message_header = (str(group_1) + ' ' + str(group_2) + ' ' + str(group_3) + ' ' + str(group_4) + ' ' +
                      date_stamp[1] + date_stamp[2] + ' ' + temp_timeforecast[0] + temp_dateforecast[0] +
                      temp_dateforecast[1] + temp_dateforecast[-1])

    message_body_lines = []

    for i in range(len(group_5)):
        message_body_lines.append(f"{group_5[i]} {group_6[i]}")
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




