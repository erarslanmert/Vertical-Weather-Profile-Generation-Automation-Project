import pandas as pd
import xarray
from numpy import array
from scipy.interpolate import interp1d

header_data = {}
table_data = {}
output_path = ""
acceptance_flag = 0

def interpolate_values(input_dict, target_heights):
    # Extract the original heights and Pc values from the input dictionary
    original_heights = input_dict['HeightE']
    original_Pc = input_dict['Pc']
    original_Dir = input_dict['Dir']
    original_Speed = input_dict['Speed']
    original_Temp = input_dict['VirtT']
    # Interpolate the Pc values for the target heights
    interpolated_Pc = interp1d(original_heights, original_Pc, fill_value='extrapolate')(target_heights)
    interpolated_Dir = interp1d(original_heights, original_Dir, fill_value='extrapolate')(target_heights)
    interpolated_Speed = interp1d(original_heights, original_Speed, fill_value='extrapolate')(target_heights)
    interpolated_virtT = interp1d(original_heights, original_Temp, fill_value='extrapolate')(target_heights)
    return [interpolated_Speed, interpolated_Dir, interpolated_virtT, interpolated_Pc]


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

def define_message():
    from datetime import datetime
    print(header_data)
    print(table_data)
    RPLat = header_data['RPLat'][0]
    RPLon = header_data['RPLon'][0]
    date = header_data['ReleaseDate'][0]
    time = header_data['ReleaseTime'][0]
    Q = determine_Q(RPLat, RPLon)
    group_1 = f'METCM{Q}'
    group_2 = format_float_to_3_digits(float(RPLat)) + format_float_to_3_digits(float(RPLon))
    parsed_date = datetime.strptime(date, '%d/%m/%y')
    day = f"{parsed_date.day:02d}"
    parsed_time = datetime.strptime(time, '%H:%M:%S')
    minute = parsed_time.minute
    minute_decimal = minute / 60
    fraction = int((minute_decimal - int(minute_decimal)) * 10)
    hour = parsed_time.hour
    group_3 = str(day) + f"{hour:02d}" + f"{fraction}0"
    height = int(header_data['RPHeightMSL'][0] / 10)
    pressure = int(header_data['GLPressure'][0]) % 1000
    data_frame = pd.DataFrame(table_data)
    zone_number_code = {
        (0,1): '00',
        (1, 200): '01',
        (200, 500): '02',
        (500, 1000): '03',
        (1000, 1500): '04',
        (1500, 2000): '05',
        (2000, 2500): '06',
        (2500, 3000): '07',
        (3000, 3500): '08',
        (3500, 4000): '09',
        (4000, 4500): '10',
        (4500, 5000): '11',
        (5000, 6000): '12',
        (6000, 7000): '13',
        (9000, 10000): '16',
        (10000, 11000): '17',
        (11000, 12000): '18',
        (12000, 13000): '19',
        (13000, 14000): '20',
        (14000, 15000): '21',
        (15000, 16000): '22',
        (16000, 17000): '23',
        (17000, 18000): '24',
        (18000, 19000): '25',
        (19000, 20000): '26',
        (20000, 22000): '27',
        (22000, 24000): '28',
        (24000, 26000): '29',
        (26000, 28000): '30',
        (28000, 30000): '31'
    }

    target_heights = array([0, 100, 350, 750, 1250, 1750, 2250, 2750, 3250, 3750, 4250, 4750, 5500, 6500, 7500, 8500, 9500,
         10500, 11500, 12500, 13500, 14500, 15500, 16500, 17500, 18500, 19500, 21000, 23000, 25000,
         27000, 29000])
    group_5 = []
    group_5_1 = []
    group_5_2 = []
    group_5_3 = []
    group_6 = []
    group_6_1 = []
    group_6_2 = []
    if height < 0:
        altitude = target_heights
    else:
        altitude = target_heights + table_data['HeightMSL'][0]

    interpolated_dictionary = interpolate_values(table_data, altitude)
    for alt in altitude:
        for (start, end), output in zone_number_code.items():
            if start <= (alt - altitude[0]) < end:
                group_5_1.append(output)

    for i in range(len(group_5_1)):
        direction = interpolated_dictionary[1][i] * 6400/360
        group_5_2.append(direction)
        group_5_3.append(interpolated_dictionary[0][i]*1.94384)
        text_5 = f"{group_5_1[i]}{int(group_5_2[i]) // 10 % 1000:03d}{int(group_5_3[i]):03d}"
        group_5.append(text_5)
        group_6_1.append(interpolated_dictionary[2][i]*10)
        group_6_2.append(interpolated_dictionary[-1][i])
        text_6 = f"{int(group_6_1[i]):04d}{int(group_6_2[i]):04d}"
        group_6.append(text_6)

    if int(interpolated_dictionary[-1][0]) >= 1000:
        formatted_string = f"{int(interpolated_dictionary[-1][0]):03d}"
        group_4 = f"{int(altitude[0]):03d}" + formatted_string[-3:]
    else:
        group_4 = f"{int(altitude[0]):03d}" + f"{int(interpolated_dictionary[-1][0]):03d}"
    message_header = str(group_1) + ' ' + str(group_2) + ' ' + str(group_3) + ' ' + str(group_4)
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



