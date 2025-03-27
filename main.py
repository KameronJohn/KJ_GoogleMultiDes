import requests
import time
from datetime import datetime, timedelta
import pytz
import re
from urllib.parse import urlparse, unquote
import os
import re
import random
import string
import pyperclip
""" 
make sure you have "api_key.txt" in the same directory.
Simpliy put the key in the file.
"""

class GoogleMap:
    def __init__(self) -> None:
        self.debugging = True 
        self.debugging = False
        self.calculation_departure = list()
        self.calculation_arrival = list()
        self.url = f"https://maps.googleapis.com/maps/api/directions/json"
        self.output = ""
        self.api_key = self.read_text_file()
    def debugger(self,msg):
        if self.debugging == True:
            print(f'[debug]'+'-'*10+f'{msg}')
    def read_text_file(self):
        """
        Reads the content of a text file and returns it as a string.

        Args:
            file_path (str): The path to the text file.

        Returns:
            str: The content of the text file.
        """
        currentPath = os.path.dirname(os.path.abspath(__file__))
        file_path = currentPath + "\\api_key.txt"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the file: {e}")
    def print_final_result(self,text):
        text = str(text)
        self.debugger(text)
        self.output = self.output + text + "\n"

    def get_distance(self, origin, destination,the_time, time_mode):
        self.print_final_result("-   -     -     -     -     -")
        # Parameters
        params = {
            "origin": origin,  # Starting location
            "destination": destination,  # Destination
            "mode": "driving",  # Travel mode (transit supports arrival_time)
            "avoid": "tolls",

            "key": self.api_key  # Replace with your Google Maps API key
        }
        if time_mode == "arrival_time":
            params["arrival_time"] = self.time_format_converter(the_time)["unix_timestamp"]
        if time_mode == "departure_time":
            params["departure_time"] = self.time_format_converter(the_time)["unix_timestamp"]
            params["traffic_model"] = "pessimistic"
        # Request directions
        response = requests.get(self.url, params=params)
        actual_url = requests.Request('GET', self.url, params=params).prepare().url
        self.debugger("Actual URL: "+ actual_url)

        # Check if the request was successful
        data = response.json()  # Parse the JSON response
        if data['status'] != 'OK':
            if data['error_message'] == "departure_time is in the past. Traffic information is only available for future and current times.":
                print(data['error_message'])
                map.da_main(the_time,place_list,time_mode)
                exit()
                # current_date = datetime.today().strftime(r'%Y-%m-%d')
            print(params)
            print(self.time_format_converter(the_time))
            print(data)  # Print the data or process it as needed
            exit()
        # Extract duration and calculate "leave by" time
        # self.print_final_result(f"params: {params}")
        # self.print_final_result(f"Duration: {data}")
        if data.get("status") == "OK":
            self.print_final_result(f"{self.extract_address_from_google_maps_url(origin)} -> {self.extract_address_from_google_maps_url(destination)}")
            if time_mode == "arrival_time":
                duration_seconds = data["routes"][0]["legs"][0]["duration"]["value"]  # Total duration in seconds
                leave_by_time = params["arrival_time"] - duration_seconds
                formatted_duration_seconds = self.format_duration(duration_seconds)
                # Convert leave_by_time to readable format
                leave_by_time_str = self.time_format_converter(leave_by_time)["time_str"]
                self.print_final_result(f"Duration: {formatted_duration_seconds}")
                self.print_final_result(f"Leave by: {leave_by_time_str}")
                self.calculation_arrival.append(leave_by_time)
                data = {
                    "origin" : origin,
                    "destination" : destination,
                    "mode" : "arrive by",
                    "time_str" : leave_by_time_str,
                    "timestamp_int" : leave_by_time
                }
                self.calculation_arrival.append(data)
            elif time_mode == "departure_time":
                duration_seconds = data["routes"][0]["legs"][0]["duration_in_traffic"]["value"]  # Total duration in seconds
                leave_by_time = params["departure_time"] + duration_seconds
                formatted_duration_seconds = self.format_duration(duration_seconds)
                # Convert leave_by_time to readable format
                leave_by_time_str = self.time_format_converter(leave_by_time)["time_str"]
                actual_leave_by_time_strrr = self.time_format_converter(leave_by_time)["unix_timestamp"] - duration_seconds
                actual_leave_by_time_strrr = self.time_format_converter(actual_leave_by_time_strrr)["time_str"]
                self.print_final_result(f"Duration: {formatted_duration_seconds}")
                self.print_final_result(f"Departing at: {actual_leave_by_time_strrr}")
                self.print_final_result(f"Arriving at: {leave_by_time_str}")
                data = {
                    "origin" : origin,
                    "destination" : destination,
                    "mode" : "depart at",
                    "time_str" : leave_by_time_str,
                    "timestamp_int" : leave_by_time
                }
                self.calculation_departure.append(data)
        self.print_final_result("Google: " + self.clean_google_maps_url(self.google_return_link(destination)))
        self.print_final_result("Waze: " + self.get_wise_link(destination))
        return leave_by_time_str, duration_seconds
    def google_return_link(self, destination):
        if destination.startswith("https://www.google.com/maps/place/"):
            # return self.extract_address_from_google_maps_url(destination)
            return destination
        else:
            return self.replace_spaces_with_plus(destination)
            return destination
    @staticmethod
    def clean_google_maps_url(url):
        try:
            return re.sub(r'/@[^/]+/.*', '', url)
        except:
            return url

    @staticmethod
    def replace_spaces_with_plus(input_string):
        """
        Replace all spaces in the input string with '+'.
        
        Args:
            input_string (str): The string to process.
        
        Returns:
            str: The modified string with spaces replaced by '+'.
        """
        return_str = "https://www.google.com/maps/place/" + input_string.replace(" ", "+")
        return return_str
    @staticmethod        
    def format_duration(duration_seconds):
        if duration_seconds < 60:
            # Less than a minute: Show only seconds
            return f"{duration_seconds}s"
        elif duration_seconds < 3600:
            # Less than an hour: Show minutes and seconds
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            return f"{minutes}m{seconds}s"
        else:
            # One hour or more: Show hours, minutes, and seconds
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            return f"{hours}h{minutes}m{seconds}s"
    def time_format(self,response):
        current_datetime = datetime.today()
        new_datetime = current_datetime + timedelta(hours=int(response[:2]), minutes=int(response[-2:]))
        unix_timestamp = int(time.mktime(new_datetime.timetuple()))
        return unix_timestamp  # Arrival time as UNIX timestamp
    def time_format_converter(self,unknown_type):
        try:
            # case 1: string
            # date_string = "07/01/2025 12:14:23"
            datetime_object = datetime.strptime(unknown_type, "%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(datetime_object.timestamp())
            time_str = unknown_type
        except TypeError as e:
            try:
                #case 2: Unix timestamp
                # Try converting a Unix timestamp to a datetime object
                datetime_object = datetime.fromtimestamp(unknown_type)
                time_str = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
                unix_timestamp = int(unknown_type)
            except TypeError as e:
                #case 3: datetime object
                datetime_object = unknown_type
                unix_timestamp = int(datetime_object.timestamp())
                time_str = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "datetime_object":datetime_object,
            "unix_timestamp":unix_timestamp,
            "time_str":time_str
        }

    def compare_times(self,original_time,target_time, calculated_time):
        """
        Compares calculated_time to target_time and returns the difference.

        Args:
            target_time (datetime): The target datetime value.
            calculated_time (datetime): The calculated datetime value to compare.

        Returns:
            dict: A dictionary with keys 'difference', 'relation', and 'adjusted_time'.
                'difference' is the absolute difference between target_time and calculated_time as a timedelta object.
                'relation' is 'larger', 'smaller', or 'equal'.
                'adjusted_time' is the target_time adjusted by the difference.
        """
        # Convert to human-readable time
        calculated_time = self.time_format_converter(calculated_time)
        self.debugger("calculated_time: "+ calculated_time["time_str"])
        target_time = datetime.strptime(target_time, "%Y-%m-%d %H:%M:%S")
        difference = calculated_time["datetime_object"] - target_time
        if isinstance(original_time, int):
            original_time = datetime.fromtimestamp(original_time)
        adjusted_time = original_time - difference
        human_readable_time = datetime.fromtimestamp(int(adjusted_time.timestamp())).strftime("%Y-%m-%d %H:%M:%S")
        if timedelta(minutes=-1)<= difference <= timedelta(minutes=1):
            return True
        elif difference > timedelta(0):
            relation = "larger"
        elif difference < timedelta(0):
            relation = "smaller"
        human_readable_time = adjusted_time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "difference": abs(difference),
            "relation": relation,
            "adjusted_time": adjusted_time
        }
        
    # Example usage
    # target_time = datetime(2025, 1, 7, 12, 0, 0)
    # calculated_time = datetime(2025, 1, 7, 14, 30, 0)
    # result = compare_times(target_time, calculated_time)
    # print(result)  # Output: {'difference': timedelta(seconds=9000), 'relation': 'larger', 'adjusted_time': datetime(2025, 1, 7, 14, 30)}
    def get_element_pairs(self,lst, the_time,time_mode):
        """
        Loops through a list and returns pairs of elements.
        
        Args:
            lst (list): The input list to process.
            descending (bool): If True, process the list in descending order.
        
        Returns:
            list: A list of tuples containing the element pairs.
        """
        if time_mode == 'arrival_time':
            lst = lst[::-1]  # Reverse the list for descending order
        
        pairs = []
        total_time = 0
        for self.i in range(len(lst) - 1):
            pairs.append((lst[self.i], lst[self.i + 1]))
            if time_mode == 'arrival_time':
                the_time, duration_seconds = self.get_distance(lst[self.i+1],lst[self.i],the_time,time_mode)
            else:
                the_time, duration_seconds = self.get_distance(lst[self.i],lst[self.i + 1],the_time,time_mode)
            total_time += duration_seconds
        self.print_final_result("-   -     -     -     -     -")
        self.print_final_result(f"stops: {self.num_of_stops}")
        self.print_final_result("total_time: " + self.format_duration(total_time))
        return pairs
    def get_wise_link(self,google_link: str):
        resolved_url = self.replace_spaces_with_plus(google_link)
        # Resolve the shortened URL
        # response = requests.head(google_link, allow_redirects=True)
        # resolved_url = response.url
        crds = self.extract_coordinates_with_regex(resolved_url)
        if not crds:
            self.debugger("get_wise_link: Trying places API")
            """  """
            cid = self.places_api_parse_cid(resolved_url)
            """  """
            crds = self.get_coordinates_from_place_id(cid, self.api_key)
        if not crds:
            crds = self.extract_coordinates_with_regex(resolved_url, last_resort=True)
        if not crds:
            crds = self.get_coordinates_from_address(google_link)
        if not crds:
            self.debugger("get_wise_link: Every attempt to get coordinates failed")
            return None
        # Extract coordinates from the path
        return self.waze_link_from_coords(crds)
    def hex_to_decimal(self,hex_string):
        # Convert using Python's int function with base 16
        try:
            return int(hex_string, 16)
        except ValueError:
            self.debugger("Invalid hexadecimal string")
            return None
    def get_coordinates_from_address(self,address):
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": self.api_key}
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            # return location["lat"], location["lng"]
            # return {"latitude": f"{latitude:.6f}", "longitude": f"{longitude:.6f}"}
            return {"latitude": f"{location['lat']:.6f}", "longitude": f"{location['lng']:.6f}"}
        return None
    def waze_link_from_coords(self,crds):
        if crds:
            latitude = crds.get("latitude")
            longitude = crds.get("longitude")
            self.debugger(f"waze_from_coords: Latitude: {latitude}, Longitude: {longitude}")
            if latitude and longitude:
                return f"https://ul.waze.com/ul?ll={latitude}%2C{longitude}&navigate=yes"
        else:
            return None
    def places_api_parse_cid(self,shitty_link):
        try:
            # Regex pattern to match latitude and longitude pairs
            self.debugger("places_api_parse_cid: Now will try resolve it as Google Place")
            self.debugger(shitty_link)
            patterns = [r"ftid.*:(\w+)",r"/data=.*0x(\w+)"]
            for pattern in patterns:
                match = re.search(pattern, shitty_link)
                if match:
                    # Extract cid in hex
                    cid_hex = match.groups()[0]
                    self.debugger(f"cid hex is: {cid_hex}")
                    if cid_hex:
                        cid = self.hex_to_decimal(cid_hex)
                        self.debugger(f"cid is: {cid}")
                    return cid
        except Exception as e:
            self.debugger(f"Error extracting cid: {e}")
        self.debugger("places_api_parse_cid: failed to parse cid")
        return None
    def extract_coordinates_with_regex(self,url, last_resort=False):
        try:
            # Sometimes /places link may contain coordinates of the location, which
            # user browsed after he chosed the destination.
            # Lets ensure we will not try to parse it.
            # Same for /dir/ locations - it is google maps directions (route).
            if not url:
                self.debugger("extract_crds: no url passed")
            if not last_resort:
                if "%C2%B0" in url:
                    self.debugger("extract_crds: passed ° symbol. Will try another regex")
                    crds = self.parse_direct_coordinates(url)
                    if crds:
                        return crds
                if "/place/" in url or "/dir/" in url:
                    self.debugger("extract_crds: it is a 'places' or 'dir' link, parsing skipped")
                    return None
            if last_resort:
                self.debugger("extract_crds_last_resort: lemme try to find any coords no matter what")

            # Regex pattern to match latitude and longitude pairs
            pattern = r"([-+]?\d+\.\d+?),\s*([-+]?\d+\.\d+)"
            match = re.search(pattern, url)
            if match:
                # Extract latitude and longitude from groups
                latitude, longitude = match.groups()
                latitude = latitude.lstrip('+')
                longitude = longitude.lstrip('+')
                self.debugger(f"extract_crds: {latitude}/{longitude}")
                return {"latitude": latitude, "longitude": longitude}
            else:
                self.debugger("extract_crds: failed to parse cords")
        except Exception as e:
            self.debugger(f"Error extracting coordinates: {e}")
        return None
    def get_coordinates_from_place_id(self,place_id, api_key):
        """
        Convert a Google Places ID to coordinates using the Places Details API.

        Args:
            place_id (str): The Google Places ID.
            api_key (str): Your Google API key.

        Returns:
            dict: A dictionary containing latitude and longitude, or None if failed.
        """
        try:
            # API endpoint for Places Details
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {"cid": place_id, "key": api_key}

            # Make the API request
            response = requests.get(url, params=params)
            response_data = response.json()

            # Check the response status
            if response_data["status"] == "OK":
                # Extract geometry location
                location = response_data["result"]["geometry"]["location"]
                return {"latitude": location["lat"], "longitude": location["lng"]}
            else:
                raise ValueError(f"Places API Error: {response_data['status']}")

        except Exception as e:
            self.debugger(f"Error resolving coordinates from Place ID: {e}")
            return None
    def parse_direct_coordinates(encoded_string):
        # Define the regex pattern for both latitude and longitude
        pattern = r"(\d+)%C2%B0(\d+)\'(\d+\.\d+)%22([NS])\+(\d+)%C2%B0(\d+)\'(\d+\.\d+)%22([EW])"
        
        # Search for matches
        match = re.search(pattern, encoded_string)
        if not match:
            return "No coordinates found in the input string."

        # Extract groups from the match
        (lat_deg, lat_min, lat_sec, lat_dir,
        lon_deg, lon_min, lon_sec, lon_dir) = match.groups()

        # Convert latitude to decimal degrees
        latitude = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
        if lat_dir == 'S':  # South means negative latitude
            latitude = -latitude

        # Convert longitude to decimal degrees
        longitude = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600
        if lon_dir == 'W':  # West means negative longitude
            longitude = -longitude

        # Return the parsed coordinates in the desired format
        return {"latitude": f"{latitude:.6f}", "longitude": f"{longitude:.6f}"}
    @staticmethod
    def extract_address_from_google_maps_url(url):
        """
        Extract the address from a Google Maps URL and remove '+' signs.

        Args:
            url (str): The Google Maps URL.

        Returns:
            str: The extracted address with '+' replaced by spaces.
        """
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Extract the address from the path
        if "/place/" in parsed_url.path:
            address = parsed_url.path.split("/place/")[-1]
            address = address.split("/@")[0]  # Remove everything after /@
            return unquote(address.replace("+", " "))
        else:
            return url
            # raise ValueError("The URL does not contain a recognizable address.")
    def input_type(self,x):
        if isinstance(x, (int, float)):
            return "Number"
        elif isinstance(x, str):
            return "String"
        elif isinstance(x, list):
            return "List"
        elif isinstance(x, dict):
            return "Dictionary"
        elif callable(x):
            return "Function"
        else:
            return "Unknown"
    def input_data_transformation(self,x):
        if self.input_type(x) == "List":
            return x
        elif self.input_type(x) == "String":
            x = self.transform(x)

            return x
        else:
            raise ValueError("Invalid input type. Please provide a list of addresses or a string.")
    def transform(self,x):
        """ 
         https://www.google.com/maps/dir/50+Ann+O'Reilly+Rd,+North+York,+ON+M2J+0C9%E5%8A%A0%E6%8B%BF%E5%A4%A7/188+Doris+Avenue,+North+York,+ON/
         66+Wickstead+Way,+Markham,+ON/
         5500+Yonge+Street,+North+York,+ON
         /Markham+Civic+Centre+Skating+Rink,+Town+Centre+Boulevard,+Markham,+ON/@43.8079525,-79.4099664,13z/
         data=!3m1!4b1!4m37!4m36!1m5!1m1!1s0x89d4d25981dac073:0x4e307e570ee94a10!2m2!1d-79.3300828!2d43.774753!1m
         5!1m1!1s0x882b2d6f05503125:0x9f7ee3cd6a33fe4b!2m2!1d-79.4106083!2d43.7674214!1m5!1m1!1s0x89d4d34239f2d51d:0x
         bcccfc5d3fcd26aa!2m2!1d-79.3598638!2d43.813794!1m5!1m1!1s0x882b2d0da1d00117:0x6e8924b76d6b1274!2m2!1d-79.4154722!2d43.7
         782504!1m5!1m1!1s0x89d4d4f8a315134d:0x189f08bb31ca852c!2m2!1d-79.3358396!2d43.8564264!2m4!2b1!6e0!7e2!8j1739687820!3e0?
         entry=ttu&g_ep=EgoyMDI1MDIxMi4wIKXMDSoJLDEwMjExNDU1SAFQAw%3D%3D
           """
        """ 
         https://www.google.com/maps/dir/50+Ann+O'Reilly+Rd,+North+York,+ON+M2J+0C9%E5%8A%A0%E6%8B%BF%E5%A4%A7/188+Doris+Avenue,+North+York,+ON/66+Wickstead+Way,+Markham,+ON/5500+Yonge+Street,+North+York,+ON/Markham+Civic+Centre+Skating+Rink,+Town+Centre+Boulevard,+Markham,+ON/@43.8079525,-79.4099664,13z/data=!3m1!4b1!4m37!4m36!1m5!1m1!1s0x89d4d25981dac073:0x4e307e570ee94a10!2m2!1d-79.3300828!2d43.774753!1m5!1m1!1s0x882b2d6f05503125:0x9f7ee3cd6a33fe4b!2m2!1d-79.4106083!2d43.7674214!1m5!1m1!1s0x89d4d34239f2d51d:0xbcccfc5d3fcd26aa!2m2!1d-79.3598638!2d43.813794!1m5!1m1!1s0x882b2d0da1d00117:0x6e8924b76d6b1274!2m2!1d-79.4154722!2d43.7782504!1m5!1m1!1s0x89d4d4f8a315134d:0x189f08bb31ca852c!2m2!1d-79.3358396!2d43.8564264!2m4!2b1!6e0!7e2!8j1739687820!3e0?entry=ttu&g_ep=EgoyMDI1MDIxMi4wIKXMDSoJLDEwMjExNDU1SAFQAw%3D%3D
           """
        pattern = r"abc"
        pattern = r"https://www\.google\.com/maps/dir/(.*?)/@"
        match = re.search(pattern, x)
        try:
            extracted_string = match.group(1)
        except:
            raise ValueError("Invalid input type. pattern not found")
        extracted_string = re.sub(r'\+*%[a-zA-Z0-9]{2}\+*', '', extracted_string)
        cleaned_list = extracted_string.replace('+', ' ').split('/')
        self.num_of_stops = len(cleaned_list)-2
        return cleaned_list  # Return cleaned string
    @staticmethod
    def generate_4_digit_or_letter():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    def da_main(self,the_time,place_list,time_mode):
        place_list = self.input_data_transformation(place_list)
        self.get_element_pairs(place_list,the_time,time_mode)
        if time_mode == "arrival_time":
            loop_arrival = datetime.fromtimestamp(self.calculation_arrival[-1]["timestamp_int"])
            while True:
                print("calculating...")
                self.output = ""
                self.get_element_pairs(place_list,loop_arrival,"departure_time")
                result = self.compare_times(loop_arrival,the_time,self.calculation_departure[-1]["timestamp_int"])
                if result is True:
                    self.debugger("self.calculation_departure: ")
                    self.debugger(self.calculation_departure)
                    # human_readable_time = datetime.fromtimestamp(loop_arrival).strftime("%Y-%m-%d %H:%M:%S")
                    # self.debugger("human_readable_timeaaa: " + human_readable_time)
                    break
                else:
                    timestamp = int(result['adjusted_time'].timestamp())
                    human_readable_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    loop_arrival = timestamp
                    self.calculation_departure.clear()
                    self.print_final_result(" ********************************\n\n"* 3)
        self.output = "\n\n\n\n" + self.output + "ref: "+self.generate_4_digit_or_letter()
        pyperclip.copy(self.output)
        print(self.output)
def real_deal(date, time, url, option):
    the_time = date + time
    map = GoogleMap()
    map.da_main(the_time,url,option)
if __name__ == "__main__":
    map = GoogleMap()
    # print(map.get_wise_link("https://www.google.com/maps/place/43%C2%B048'48.7%22N+79%C2%B014'53.3%22W/@43.8135311,-79.25052,18z/data=!4m8!1m3!11m2!2sHd5PxpIZVzYZxQSnXyO7FVuUlvq4Cg!3e3!3m3!8m2!3d43.8135311!4d-79.2481382?authuser=0&entry=ttu&g_ep=EgoyMDI1MDMxMi4wIKXMDSoJLDEwMjExNDU1SAFQAw%3D%3D"))
    # place_list = [
    # r"50 Ann O'Reilly Rd, North York",
    # r"188 Doris Ave, North York, ON M2N 6Z5",
    # r"5500 Yonge St, Toronto, ON M2N 7L1",
    # r"66 Wickstead Way, Thornhill, ON L3T 5E5",
    # r"Markham Civic Centre Skating Rink, 171 Town Centre Blvd, Markham, ON L3P 7V1"
    # ]
    # place_list = r"https://www.google.com/maps/dir/50+Ann+O'Reilly+Rd,+North+York,+ON+M2J+0C9%E5%8A%A0%E6%8B%BF%E5%A4%A7/188+Doris+Avenue,+North+York,+ON/66+Wickstead+Way,+Markham,+ON/5500+Yonge+Street,+North+York,+ON/Markham+Civic+Centre+Skating+Rink,+Town+Centre+Boulevard,+Markham,+ON/@43.8079525,-79.4099664,13z/data=!3m1!4b1!4m37!4m36!1m5!1m1!1s0x89d4d25981dac073:0x4e307e570ee94a10!2m2!1d-79.3300828!2d43.774753!1m5!1m1!1s0x882b2d6f05503125:0x9f7ee3cd6a33fe4b!2m2!1d-79.4106083!2d43.7674214!1m5!1m1!1s0x89d4d34239f2d51d:0xbcccfc5d3fcd26aa!2m2!1d-79.3598638!2d43.813794!1m5!1m1!1s0x882b2d0da1d00117:0x6e8924b76d6b1274!2m2!1d-79.4154722!2d43.7782504!1m5!1m1!1s0x89d4d4f8a315134d:0x189f08bb31ca852c!2m2!1d-79.3358396!2d43.8564264!2m4!2b1!6e0!7e2!8j1739687820!3e0?entry=ttu&g_ep=EgoyMDI1MDIxMi4wIKXMDSoJLDEwMjExNDU1SAFQAw%3D%3D"
    # place_list = input("put link\n")
    # place_list = r"place_list"
    place_list = input("Enter the Google Maps URL: ")
    the_time = "2025-03-29 23:59:00"
    time_mode = "departure_time"
    time_mode = "arrival_time"
    map.da_main(the_time,place_list,time_mode)
    # map.get_distance()