import csv


def read_csv(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        all_values = list(reader)
        return all_values

