from __future__ import print_function
from googleapiclient.discovery import build

from src.config import SAMPLE_SPREADSHEET_ID, SHEET_HIDDEN_TO_SEARCH
from common_python.utils import google_init_creds, error_wrapper


def is_sheet_empty(spreadsheet_id=SAMPLE_SPREADSHEET_ID):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range='A1').execute()
    values = result.get('values', [])

    return not values


@error_wrapper
def get_spreadsheet(sheet_id):

    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    request = service.spreadsheets().get(spreadsheetId=sheet_id, ranges=[], includeGridData=False)
    response = request.execute()

    return response


@error_wrapper
def append_line(sheet_id, row):

    creds = google_init_creds()
    service = build('sheets', 'v4', credentials=creds)

    # TODO add SheetName to range
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range='A1',
        valueInputOption='RAW', body={"values": [row]}).execute()

    return result


@error_wrapper
def create_new_sheet(spreadsheet_id, new_sheet_name):

    creds = google_init_creds()
    request_body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': new_sheet_name,
                    'hidden': True
                }
            }
        }]
    }

    service = build('sheets', 'v4', credentials=creds)

    result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()

    return result


def create_spreadsheet(title='NewMy1234'):

    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_body = {
        'properties': {
            'title': title
        }
    }

    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()

    return response['spreadsheetId']


def find_row_num_by_value(target="user@gmial.com", sheet_name="Sheet1", col_name="A",
                          sample_spreadsheet_id=SAMPLE_SPREADSHEET_ID):
    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = sample_spreadsheet_id  # TODO: Update placeholder value.

    # The A1 notation of the values to update.
    range_ = SHEET_HIDDEN_TO_SEARCH + '!A1'  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.

    value_range_body = {
        "range": range_,
        "values": [['=MATCH("{search}", {sheetName}!{colName}:{colName}, 0)'.format(
            search=target, sheetName=sheet_name, colName=col_name)]]
    }

    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, includeValuesInResponse=True,
                                                     responseValueRenderOption='UNFORMATTED_VALUE', range=range_,
                                                     valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    return response


def find_positions_by_values(search_formulas, sample_spreadsheet_id=SAMPLE_SPREADSHEET_ID):
    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = sample_spreadsheet_id  # TODO: Update placeholder value.

    # The A1 notation of the values to update.
    range_ = SHEET_HIDDEN_TO_SEARCH + '!A1'  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.

    value_range_body = {
        "range": range_,
        "values": [search_formulas]
    }

    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, includeValuesInResponse=True,
                                                     responseValueRenderOption='UNFORMATTED_VALUE', range=range_,
                                                     valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    return response


def find_header_column_indexes(headers: [str], spreadsheet_id: str, sheet_name: str) -> [(str, int)]:
    search_formulas = ['=MATCH("{search}"; {sheetName}!{colName}:{colName}; 0)'.format(
        search=header_name, sheetName=sheet_name, colName='1') for header_name in headers]

    response = find_positions_by_values(search_formulas, spreadsheet_id)

    indexes = response['updatedData']['values'][0]

    result = list(zip(headers, indexes))

    return result


def find_row_index(value, column_letter, spreadsheet_id: str, sheet_name: str) -> int:
    search_formulas = ['=MATCH({search}; {sheetName}!{colName}:{colName}; 0)'.format(
        search=value, sheetName=sheet_name, colName=column_letter)]

    response = find_positions_by_values(search_formulas, spreadsheet_id)

    index = response['updatedData']['values'][0][0]

    return index


def batch_update(entries_to_update, sample_spreadsheet_id=SAMPLE_SPREADSHEET_ID):
    creds = google_init_creds()

    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = sample_spreadsheet_id  # TODO: Update placeholder value.

    # The A1 notation of the values to update.
    range_ = SHEET_HIDDEN_TO_SEARCH + '!A1'  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.

    data = []
    for rangeName, rangeValue in entries_to_update.items():
        data.append({
            "range": rangeName,
            "values": [[rangeValue]]
        })

    batch_update_values_request_body = {
        # How the input data should be interpreted.
        'value_input_option': 'RAW',  # TODO: Update placeholder value.
        'response_value_render_option': 'UNFORMATTED_VALUE',
        'include_values_in_response': True,
        # The new values to apply to the spreadsheet.
        'data': data
    }

    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                          body=batch_update_values_request_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    return response


if __name__ == '__main__':
    # is_sheet_empty()
    res = find_row_num_by_value()
    print(res['updatedData']['values'][0][0])
