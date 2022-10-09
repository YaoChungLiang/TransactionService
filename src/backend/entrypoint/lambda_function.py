import json
import boto3
from collections import defaultdict
from datetime import datetime as dt

dynamodb = boto3.resource('dynamodb')
TRANSACTION_TABLE = 'Transaction'
INF_TIME='9999-12-31T23:59:59Z'

def lambda_handler(event, context):
    method = event['requestContext']['http']['method']
    body = json.loads(event.get('body', '{}'))
    query = event.get('queryStringParameters', dict()) 

    resp = success_formatter('No functions be triggered in the backend , please provide the valid inputs') 
    if method == 'POST' and 'delete_all' in body:
        resp = delete_all_records(TRANSACTION_TABLE)
    elif method == 'POST' and 'payer' in body:
        resp = insert_data_to_dynamoDB(TRANSACTION_TABLE, **(body))
    elif method == 'POST' and 'data_list' in body:
        resp = batch_write_items(TRANSACTION_TABLE, body['data_list'])
    elif method == 'POST' and 'points' in body:
        resp = force_payers_to_pay(TRANSACTION_TABLE, **(body))
    elif method == 'GET' and 'balance' in query:
        resp = get_balance(TRANSACTION_TABLE)
    return resp

def force_payers_to_pay(table_name, *args, **kwargs):
    request_points = kwargs.get('points')
    if request_points < 1:
        return exception_formatter(f'Request_points {request_points} should not be less than 1', 409)
    points_can_spend_dict = get_points_can_spend_dict(table_name)
    sorted_records = get_sorted_records(table_name)
    max_points_can_pay = sum([record[2] for records in points_can_spend_dict.values() for record in records])
    now_timestamp = dt.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    money_spend_record = []
    print(f'{request_points > max_points_can_pay}')
    if max_points_can_pay < request_points:
        return exception_formatter(f'Not affordable the request points {request_points}', 409)
    for record in sorted_records:
        payer = record.get('payer')
        timestamp = record.get('timestamp')
        if request_points == 0:
            break
        if len(points_can_spend_dict[payer]) > 0 and points_can_spend_dict[payer][0][0] <=  timestamp < points_can_spend_dict[payer][0][1]:
            points_spend = min(points_can_spend_dict[payer][0][2], request_points)
            if points_spend == 0:
                continue
            money_spend_record.append({'payer': payer, 'points': -1 * points_spend, 'timestamp': now_timestamp})
            points_can_spend_dict[payer].pop(0)
            request_points -= points_spend
    resp = batch_write_items(table_name, money_spend_record)
    for record in money_spend_record:
        del record['timestamp']
    return money_spend_record


def batch_write_items(table_name, records):
    table = dynamodb.Table(table_name)
    with table.batch_writer() as writer:
        for item in records:
            writer.put_item(Item=item)
    return success_formatter('Success batch wirte the items', 201)

    
def get_points_can_spend_dict(table_name):
    records = get_records(table_name)
    points_can_spend_dict = dict() # payer : queue[[st_timestamp, end_timestamp, max_money]]
    for record in records:
        payer = record.get('payer')
        points = record.get('points')
        timestamp = record.get('timestamp')
        if payer not in points_can_spend_dict:
            points_can_spend_dict[payer] = [[timestamp, INF_TIME, points]]
        elif points < 0:
            points_can_spend_dict[payer][-1][1] = timestamp
            points_can_spend_dict[payer][-1][2] += points
        else:
            points_can_spend_dict[payer][-1][1] = timestamp
            points_can_spend_dict[payer].append([timestamp, INF_TIME, points])
    
        # clean up, make sure the last record last forever
        for payer, record in points_can_spend_dict.items():
            record[-1][1] = INF_TIME
    return points_can_spend_dict


def delete_all_records(table_name):
    table = dynamodb.Table(table_name)
    scan = table.scan()
    with table.batch_writer() as batch:
        for record in scan['Items']:
            batch.delete_item(
                Key={
                    'payer': record['payer'],
                    'timestamp': record['timestamp']
                }
            )
    resp = f'Deleted all data in the table {table_name}'
    return success_formatter(resp)

def get_sorted_records(table_name):
    print('RUNNING get sorted records')
    all_records = get_records(table_name)
    all_records.sort(key=lambda x: x.get('timestamp'))
    return all_records

    
def get_records(table_name):
    table = dynamodb.Table(table_name)
    data = table.scan()['Items']
    print(f'Items in the table {table_name} : {data}')
    return data


def get_balance(table_name):
    table = dynamodb.Table(table_name)
    data = table.scan()['Items']
    balance = defaultdict(int)
    for record in data:
        balance[record['payer']] += record['points']
    print(f'Balance in the table {table_name} : {balance}')
    return balance

def insert_data_to_dynamoDB(table_name, *args, **kwargs):
    table = dynamodb.Table(table_name)
    print(f'I got kwargs {kwargs} ')
    response = table.put_item(Item=kwargs)
    return response


def success_formatter(resp, status_code=200):
    print("Success response : {}".format(str(resp)))
    responseObj = {}
    responseObj['StatusCode'] = 200
    responseObj['headers'] = {'Content-Type': 'application/json'}
    responseObj['body'] = json.dumps(resp)
    return responseObj


def exception_formatter(e, status_code=400):
    print("Exception occured : {}".format(str(e)))
    responseObj = {}
    responseObj['StatusCode'] = status_code
    responseObj['headers'] = {'Content-Type': 'application/json'}
    responseObj['body'] = {'error': str(e)}
    return responseObj

