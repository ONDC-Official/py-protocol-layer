import csv
import os

city_to_pin_codes = {}


def get_city_to_pin_codes_mapping():
    global city_to_pin_codes
    if bool(city_to_pin_codes):
        create_city_to_pin_codes_mapping()
    return city_to_pin_codes


def create_city_to_pin_codes_mapping():
    global city_to_pin_codes
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'main/resources/city_to_pincode.csv')
    with open(filename, mode='r') as file:
        csv_file = csv.reader(file)
        for i, lines in enumerate(csv_file):
            if i != 0:
                current_pin_codes = city_to_pin_codes.get(lines[3], [])
                current_pin_codes.append(lines[0])
                city_to_pin_codes[lines[3]] = current_pin_codes
