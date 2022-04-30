import csv
from collections import defaultdict
from datetime import datetime

import boto3
import openpyxl
import sqlalchemy
from dateutil.parser import parse
from funcy import merge
from sqlalchemy.orm import Session

from main.aws_event_handler.utils import get_attachment_from_email_data
from main.bulk.csv_utils import read_csv
from main.config import get_config_value_for_name
from main.controller.fairmatic_redshift_controller.fairmatic_claims_table import BroadSpireClaimsData, Base, \
    ProductLinks, LossType
from main.controller.utils import create_random_string
from main.logger.custom_logging import log
from main.utils.function_decorators import MeasureTime

s3_client = boto3.client('s3')


def get_engine():
    engine = sqlalchemy.create_engine(f'{get_config_value_for_name("CLAIMS_REDSHIFT_SQLALCHEMY_URI")}', )
    return engine


def format_column_name(column_name: str):
    return column_name.lower().replace(" ", "_").replace("?", "").replace("/", "_")


def rename_columns(row_dictionary):
    return {format_column_name(key): value.strip() for key, value in row_dictionary.items()}


def parse_date_if_column_is_date(key, value):
    try:
        if value in ["", None]:
            return None
        if key.endswith('date'):
            return parse(value)
        else:
            return value
    except:
        print(f"error in {key} & {value}")


def parse_date_columns(row):
    return {key: parse_date_if_column_is_date(key, value) for key, value in row.items()}


def convert_xlsx_to_csv(local_file_path):
    wb = openpyxl.load_workbook(local_file_path)
    sh = wb.active
    tempfile = f"/tmp/{create_random_string()}.csv"
    with open(tempfile, 'w', newline="") as f:
        c = csv.writer(f)
        for r in sh.rows:
            c.writerow([cell.value for cell in r])
    return tempfile


def convert_to_db_claims_object(row):
    broadsprire_claims_row = BroadSpireClaimsData(**row)
    return broadsprire_claims_row

def convert_to_db_product_link_object(row):
    broadsprire_product_row = ProductLinks(**row)
    return broadsprire_product_row

def convert_to_db_loss_type_object(row):
    broadsprire_loss_row = LossType(**row)
    return broadsprire_loss_row


def add_todays_date(row_dictionary):
    return merge(row_dictionary,{"insertion_date": datetime.now()})


@MeasureTime
def process_broadspire_csvs(session, local_file_path):
    csv_file = convert_xlsx_to_csv(local_file_path)
    rows = read_csv(csv_file)
    log(f"[BROADSPIRE_CSV]read {len(rows)} from csv")
    rows = list(map(rename_columns, rows))
    rows = list(map(parse_date_columns, rows))
    rows = list(map(add_todays_date,rows))
    log(f"[BROADSPIRE_CSV]filtered {len(rows)} from csv")
    session.add_all(map(convert_to_db_claims_object, rows))
    log(f"[BROADSPIRE_CSV]committing {len(rows)} from csv")
    session.commit()
    log(f"[BROADSPIRE_CSV]committed {len(rows)} from csv")


@MeasureTime
def process_broadspire_product_link(session,csv_file):
    rows = read_csv(csv_file)
    log(f"[BROADSPIRE_CSV]read {len(rows)} from csv")
    session.add_all(map(convert_to_db_product_link_object, rows))
    log(f"[BROADSPIRE_CSV]committing {len(rows)} from csv")
    session.commit()

@MeasureTime
def process_broadspire_loss_type(session,csv_file):
    rows = read_csv(csv_file)
    log(f"[BROADSPIRE_CSV]read {len(rows)} from csv")
    session.add_all(map(convert_to_db_loss_type_object, rows))
    log(f"[BROADSPIRE_CSV]committing {len(rows)} from csv")
    session.commit()


def get_processor_function_for_bucket_and_key(bucket, key):
    if bucket == "fm-ses-inbox" and key.startswith("broadspire-ses-in/v1/"):
        return process_broadspire_csvs


def safe_create(engine,tablename):
    try:
        log(f"creating table")
        Base.metadata.tables[f"{get_config_value_for_name('CLAIMS_REDSHIFT_SCHEMA')}.{tablename}"]\
            .create(bind=engine)
    except Exception as e:
        log(f"{e}")


def process_upload_function(event, context):
    """
    Process a file upload.
    """
    engine = get_engine()
    session = Session(engine)
    session.execute(f"SET search_path TO {get_config_value_for_name('CLAIMS_REDSHIFT_SCHEMA')}")
    log(f"event received is {event}")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    log(f"[s3-event]got the new uploads in bucket {bucket} at {key}")
    s3_client.download_file(bucket, key, '/tmp/email_content')
    with open('/tmp/email_content') as file:
        file_content = file.read()
    xlsx_file = get_attachment_from_email_data(file_content)
    process_broadspire_csvs(session, xlsx_file)


def adhoc_s3_broadspire_insertion(s3_email_id):
    mdefaultdict = {}
    mdefaultdict['Records'] = [{"s3": {"bucket": {"name": "fm-ses-inbox"},
                                       "object": {
                                           "key": f"broadspire-ses-in/v1/{s3_email_id}"}}}]
    process_upload_function(mdefaultdict, None)


if __name__ == '__main__':
    engine = get_engine()
    session = Session(engine)
    session.execute(f"SET search_path TO {get_config_value_for_name('CLAIMS_REDSHIFT_SCHEMA')}")
    # # safe_create(engine,"broadspire_claims_data")
    process_broadspire_loss_type(session,"/Users/navdeepagarwal/projects/git-projects/fairmatic-dashbaord/webserver/loss_types.csv")

    # process_broadspire_csvs(session, "/tmp/attach.xlsx")
    # mdefaultdict = {}
    # mdefaultdict['Records'] = [{"s3": {"bucket": {"name": "fm-ses-inbox"},
    #                                    "object": {
    #                                        "key": "broadspire-ses-in/v1/ktg20la71e83tp2r6n0el1hcp8lml2cedqfgocg1"}}}]
    # process_upload_function(mdefaultdict, None)

