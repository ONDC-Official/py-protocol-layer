import csv
from itertools import chain

from main.logger.custom_logging import log
from main.service.login import create_user
from main.utils.file_utils import get_path_for_current_file


def read_csv(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        all_values = list(reader)
        return all_values


def read_csv_and_get_schedules_rates(csv_path="sample_scheduled_rate.csv", funtion=lambda x: x):
    csv_path = get_path_for_current_file(csv_path)
    rows = read_csv(csv_path)
    responses = list(map(funtion, rows))
    rates = list(chain(*responses))
    return rates

