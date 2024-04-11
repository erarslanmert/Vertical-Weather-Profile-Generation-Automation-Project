import geopy
import requests
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz
from datetime import datetime, timedelta
import re


utc_time_zone = ''
coordinates_input = []

def get_utc_time_from_coordinates(coordinates):
    global utc_time_zone, coordinates_input
    try:
        latitude, longitude = coordinates

        # Reverse geocode to get precise location information
        geolocator = Nominatim(user_agent="get_utc_time_from_coordinates")
        location = geolocator.reverse((latitude, longitude), language='en')

        if location is None:
            return "Unable to determine location for the given coordinates."

        # Extract city name or use the fallback if not available
        city_name = location.raw.get('address', {}).get('city', 'Unknown City')

        # Find the timezone using the coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        if timezone_str is None:
            return "Unable to determine timezone for the given coordinates."

        # Get the current time in the found timezone
        local_time = datetime.now(pytz.timezone(timezone_str))

        # Get the UTC offset in hours and minutes
        utc_offset = local_time.utcoffset().total_seconds() / 3600

        # Check for daylight saving time and adjust the UTC offset
        if local_time.dst():
            utc_offset -= 1
        zone_list = timezone_str.split('/')
        zone = zone_list[0]
        if city_name == 'Unknown City':
            output = f"{timezone_str} UTC{' + ' if utc_offset >= 0 else ' - '}{abs(int(utc_offset)):02d}:{int((abs(utc_offset) % 1) * 60):02d}"
        else:
            output = f"{zone +'/'+city_name} UTC{' + ' if utc_offset >= 0 else ' - '}{abs(int(utc_offset)):02d}:{int((abs(utc_offset) % 1) * 60):02d}"
        utc_time_zone = output

    except TimeoutError:
        pass


def convert_to_utc_with_offset(input_date_str, offset_str):
    # Define input date format
    input_date_format = "%d/%m/%y %H:%M:%S"

    # Parse input date string
    input_datetime = datetime.strptime(input_date_str, input_date_format)

    # Parse the offset string
    offset_match = re.match(r"UTC\s*([+-])\s*(\d{1,2}):?(\d{0,2})", offset_str)
    if offset_match:
        sign, hours, minutes = offset_match.groups()
        sign_multiplier = -1 if sign == "-" else 1
        offset = timedelta(hours=int(hours) * sign_multiplier, minutes=int(minutes) * sign_multiplier)
    else:
        raise ValueError("Invalid offset string format")

    # Apply the offset to the input date and time
    input_datetime = input_datetime - offset

    # Format the UTC date and time
    output_date_format = "%d/%m/%y %H:%M:%S"
    output_date_str = input_datetime.strftime(output_date_format)

    return output_date_str



