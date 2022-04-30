from functools import partial

from flask import request
from flask_jwt_extended import get_jwt_identity

from main.config import Config
from main.utils.encryption import encrypt_objects, decrypt_objects
from main.utils.file_utils import create_directory, safe_delete
from main.utils.parallel_processing_utils import ioBoundParallelComputation
from main.utils.utils_s3 import create_presigned_url, upload_file, download_file, upload_file_stream
import uuid
from datetime import datetime


def get_s3_documents_prefix(*prefixes):
    return f"{'/'.join(prefixes)}"


def get_path_from_user_id_and_application_id(user_id, token_number, file_parameter_name, filename):
    return f"{user_id}/{token_number}/{file_parameter_name}/{filename}"


def get_historical_path_from_user_id_and_application_id(user_id, token_number, file_parameter_name, filename):
    return f"history/{user_id}/{token_number}/{int(datetime.now().timestamp())}/{file_parameter_name}/{filename}"


def upload_file_with_generated_path(user_id, application_id, file_paramater_name, file, save_to_history=True):
    temp_path = f"/tmp/{uuid.uuid4()}"
    create_directory(temp_path)
    temp_file_path = f"{temp_path}/{file.filename}"
    file.save(temp_file_path)
    upload_file(temp_file_path, Config.S3_PRIVATE_BUCKET,
                get_path_from_user_id_and_application_id(user_id, application_id, file_paramater_name, file.filename),
                delete=False)
    if save_to_history:
        upload_file(temp_file_path, Config.S3_PRIVATE_BUCKET,
                    get_historical_path_from_user_id_and_application_id(user_id, application_id, file_paramater_name,
                                                                        file.filename))
    safe_delete(temp_file_path)
    return get_path_from_user_id_and_application_id(user_id, application_id, file_paramater_name, file.filename)


def upload_request_file(userid, application_id, file_paramater_name, fileBytesIO, filename):
    s3_path = get_path_from_user_id_and_application_id(userid, application_id, file_paramater_name, filename)
    upload_file_stream(fileBytesIO, Config.S3_PRIVATE_BUCKET, s3_path)
    return s3_path


def upload_request_files(userid, application_id, file_paramater_name):
    uploaded_files = request.files.getlist(file_paramater_name)
    return ioBoundParallelComputation(
        partial(upload_file_with_generated_path, userid, application_id, file_paramater_name), uploaded_files)


def get_path_from_file_object(file_object):
    tempfile = f"/tmp/{file_object.split('/')[-1]}"
    download_file(file_object, Config.S3_PRIVATE_BUCKET, tempfile)
    return tempfile


def get_signed_urls_for_user(**kwargs):
    identity = get_jwt_identity()
    required_docs_files = upload_request_files(identity, kwargs["application_no"], "required_documents")

    return {"identity": identity,
            "required_documents": [create_presigned_url(Config.S3_PRIVATE_BUCKET, file, 300) for file in
                                   required_docs_files],
            "actuals":required_docs_files}


# def update_with_uploaded_list(**kwargs):
#     files = decrypt_objects(kwargs["uploaded_docs"])
#     apply_for_application(kwargs["user_id"], kwargs["token_number"], files["required_documents"],files["application_form"], kwargs["branch_id"],
#                           kwargs["amount"],kwargs["user_type"],kwargs['meta'],kwargs["phone_number"],kwargs['bank_name'])
#     # send sms to user phone number
#     send_sms(('+91' + kwargs.get("phone_number",None)), get_sms_template("NEW_LOAN_APPLICATION").format(**{"token_number": kwargs["token_number"]}))
#     # Email to bank
#     branch_info = get_branch_from_branch_id(kwargs["branch_id"])
#
#     delete_if_OTP_preset(**project(kwargs,["otp", "phone_number"]))
#     return kwargs["token_number"]