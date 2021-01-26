import csv
import http.client
import json
import os
import os.path
import pickle
import traceback
import uuid
import datetime
import urllib.parse

# import pandas as pd
# import xlsxwriter
from enum import Enum, auto

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import VERIMAIL_API_KEY, SCOPES, DEFAULT_TOKEN_PATH


def error_wrapper(func):
    """Decorator that suppress error."""

    def wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            traceback.print_exc()
            return None
    return wrap


def exception_wrapper_with_default_value(func, default_value):
    try:
        return func()
    except Exception as e:
        traceback.print_exc()
        return default_value


def verify_email(email: str) -> dict:
    conn = http.client.HTTPSConnection("api.verimail.io")
    email_encoded = urllib.parse.urlencode({'email': email})
    url = '/v3/verify?' + email_encoded + '&key=' + VERIMAIL_API_KEY
    conn.request("GET", url)
    res = conn.getresponse()
    datajs = res.read()
    data = json.loads(datajs.decode("utf-8"))
    return data


def verify_email_post(email: str) -> dict:
    conn = http.client.HTTPSConnection("api.verimail.io")
    url = '/v3/verify'
    conn.request("POST", url, json.dumps({'email': email, 'key': VERIMAIL_API_KEY}))
    res = conn.getresponse()
    datajs = res.read()
    data = json.loads(datajs.decode("utf-8"))
    return data


def construct_emails(full_name: str, domain_name: str) -> [str]:
    parts = full_name.lower().split()
    suffix = '@' + domain_name

    if len(parts) < 2:
        return [parts[0] + suffix]

    first_name = parts[0]
    last_name = parts[1]
    return [last_name + suffix,
            first_name + '.' + last_name + suffix,
            first_name[0] + '.' + last_name + suffix,
            first_name + '_' + last_name + suffix,
            first_name[0] + last_name + suffix]


def save_to_csv(headers, list_of_rows, file_name, ):
    with open(file_name, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)  # write the header
        for row in list_of_rows:
            writer.writerow(row)


# def save_to_excel(headers, list_of_rows, last_page, start_page, xlsx_file_name_suffix):
#     file_name = "{start}-{end}--{utcnow}--{suffix}" \
#         .format(start=start_page, end=last_page,
#                 utcnow=datetime.utcnow().isoformat(), suffix=xlsx_file_name_suffix)
#     workbook = xlsxwriter.Workbook(file_name)
#     worksheet = workbook.add_worksheet()
#
#     row_index = 0
#     col_index = 0
#
#     for header in headers:
#         worksheet.write(row_index, col_index, header)
#         col_index += 1
#
#     row_index = 1
#     for row in list_of_rows:
#         col_index = 0
#         for val in row:
#             worksheet.write(row_index, col_index, val)
#             col_index += 1
#         row_index += 1
#
#     workbook.close()


# todo refactor
def find_valid_email(emails: [str]) -> ([str], str):
    for email in emails:
        res = exception_wrapper_with_default_value(lambda: verify_email(email), {'deliverable': False})
        if res['deliverable'] is True:
            if res['result'] == 'deliverable':
                return [email], 'deliverable'
            elif res['result'] == 'catch_all':
                return emails, 'catch_all'
    return [], 'undeliverable'


# def merging_all_xlsx_in_dir(path: str, final_name: str) -> None:
#     files = os.listdir(path)
#     df = pd.DataFrame()
#     for file in files:
#         if file.endswith('.xlsx'):
#             df = df.append(pd.read_excel(file), ignore_index=True)
#     df.head()
#     df.to_excel(final_name, index=False)


def format_date(obj: datetime) -> str:
    """Needed for google sheets date format"""
    return obj.strftime("%d.%m.%Y %H:%M")


def google_init_creds(token_pickle_path=DEFAULT_TOKEN_PATH):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    pickle_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + token_pickle_path
    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/src/credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(pickle_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def generate_uuid():
    return str(uuid.uuid4())


class GoogleContact:
    HEADERS = ["Name", "Given Name", "Additional Name", "Family Name", "Yomi Name", "Given Name Yomi",
               "Additional Name Yomi",
               "Family Name Yomi", "Name Prefix", "Name Suffix", "Initials", "Nickname", "Short Name", "Maiden Name",
               "Birthday",
               "Gender", "Location", "Billing Information", "Directory Server", "Mileage", "Occupation", "Hobby",
               "Sensitivity",
               "Priority", "Subject", "Notes", "Language", "Photo", "Group Membership", "E-mail 1 - Type",
               "E-mail 1 - Value",
               "Phone 1 - Type", "Phone 1 - Value", "Website 1 - Type", "Website 1 - Value"]

    def __init__(self, name: str, email: str, website: str, groups: list, occupation: str) -> None:
        self.map = {
            GoogleContact.HEADERS[0]: name,
            GoogleContact.HEADERS[20]: occupation,
            GoogleContact.HEADERS[28]: " ::: ".join(groups),
            GoogleContact.HEADERS[30]: email,
            GoogleContact.HEADERS[34]: website
        }

    def to_csv_row(self) -> str:
        return ",".join([self.map[x] if self.map[x] is not None else '' for x in GoogleContact.HEADERS])


# def to_str_list(obj):
#     return [SheetContactRow.format_str(getattr(obj, name)) for name in SheetContactRow.get_field_names_ordered()]


def format_str(value: object = ''):
    if value is None:
        return ''

    value_type = type(value)
    if value_type is str:
        return value
    elif value_type is datetime.datetime:
        return format_date(value)
    else:
        return value


def get_field_names_ordered(clazz):
    return list(filter(
        lambda element:
        element.startswith('user') or element.startswith('company') or element.startswith('message'),
        clazz.__dict__.keys()))


def to_row(obj: object, clazz: type) -> {str, object}:
    result = {}
    table_name = obj.__class__.__name__
    for key, value in obj.__data__.items():
        if not key.startswith("__"):
            result[table_name + "_" + key] = value

    for key, value in obj.__rel__.items():
        if isinstance(value, clazz):
            result = {**result, **to_row(value, clazz)}
    return result


def format_row(input_arg: {str: object}, headers: [str]) -> [str]:
    return [format_str(input_arg[header]) if header in input_arg else "" for header in headers]


class UserStatus(Enum):
    EMAIL_MUST_SENT = auto()
    EMAIL_SENT = auto()
    EMAIL_OPENED = auto()
    EMAIL_OPENED_BUT_BLOCKED = auto()
    EMAIL_SEND_ERROR = auto()
    EMAIL_SEND_ERROR_ADDRESS_NOT_FOUND = auto()
    EMAIL_SEND_ERROR_BLOCKED = auto()
    EMAIL_SEND_ERROR_LIMIT = auto()
    EMAIL_CHECKING_STATUS = auto()
    EMAIL_SEND_ERROR_GENERAL = auto()
    EMAIL_RESPONDED = auto()
    LINKED_SENT_INVITE = auto()
    LINKED_SALES_SENT_MESSAGE = auto()
    LINKED_SALES_OPENED_MESSAGE = auto()
    LINKED_SALES_RESPONDED_ON_MESSAGE = auto()
    UPCOMING_CALL = auto()
    LINKED_CONFIRMED_FRIEND_REQUEST = auto()
    PITCH_CALL = auto()

