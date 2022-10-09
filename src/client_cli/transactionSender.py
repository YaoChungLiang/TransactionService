#!/usr/bin/env python

import requests
import argparse
from datetime import datetime
import json

URL = "https://5fw6uwiwsqugqyxo5ojrq5y26y0gvaxn.lambda-url.us-west-2.on.aws/"
DEFAULT_TEST_DATA = [{ "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
                { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
                { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
                { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
                { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }
              ]


# 201 : resource created
# 202 : request accepted but not yet completed
# 204 : delete stuff successful and no content needs to be returned
# 400 : invalid data into the request
# 409 : cannot update the resource


def create_record(payer, points, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    data = {'payer': payer, 'points': points, 'timestamp': str(timestamp)}
    resp = requests.post(url=URL, json=data)
    print(resp.json())
    return resp.json()

def batch_create_record(data):
    timestamp = datetime.utcnow()
    for item in data:
        if 'timestamp' not in item:
            item['timestamp'] = timestamp
    data_dict = {'data_list': data}
    resp = requests.post(url=URL, json=data_dict)
    return resp.json()


def spend_points(points):
    data = {'points':points}
    resp = requests.post(url=URL, json=data)
    print(resp.json())
    return resp.json()

def show_balance():
    params = {'balance': True}
    resp = requests.get(url=URL, params=params)
    print(json.dumps(resp.json(), indent=2))
    return resp.json()

def delete_all_records():
    print('RUNNING spend points method')
    data = {'delete_all': True}
    resp = requests.post(url=URL, json=data)
    print(resp.json())
    return resp.json()

def init_test_data(data=None):
    delete_all_records()
    if not data:
        data = DEFAULT_TEST_DATA
    resp = batch_create_record(data)
    print(resp)
    return resp

def run_test():
    resp = init_test_data()
    assert(resp['StatusCode'] == 200)
    resp = spend_points(5000)
    expect_result = [{'payer': 'DANNON', 'points': -100}, {'payer': 'UNILEVER', 'points': -200}, {'payer': 'MILLER COORS', 'points': -4700}]
    assert(resp == expect_result)
    resp = show_balance()
    expect_result = { "UNILEVER": 0, "MILLER COORS": 5300, "DANNON": 1000}
    assert(resp == expect_result)


     

if __name__ == '__main__':
    '''
    Usage:
       python transactionSender.py --insert-record --payer DEBO --points 300
       python3 transactionSender.py --delete-all
       python3 transactionSender.py --init-test-data
       python3 transactionSender.py --spend-points --points 5000
       python3 transactionSender.py --show-balance
    '''
    parser = argparse.ArgumentParser(description='Send request to Transaction Lambda service')
    #parser.add_argument('--method', type=str, help="HTTP request method, ex: delete, get, head, patch, post, put ", required=False)
    parser.add_argument('--payer', type=str, help="Payer Name, ex: DANNON", required=False)
    parser.add_argument('--timestamp', type=str, help="The Zulu Time (GMT), ex: 2020-11-02T14:00:00Z", required=False)
    parser.add_argument('--points', type=int, action="store", help="The points, ex: 100", required=False)
    parser.add_argument('--show-balance', action='store_true', default=False, help="Get the balance of each payers", required=False)
    parser.add_argument('--delete-all', action='store_true', default=False, help="Get the balance of each payers", required=False)
    parser.add_argument('--init-test-data', action='store_true', default=False, help="Initialize the data", required=False)
    parser.add_argument('--insert-record', action='store_true', default=False, help="Insert record from user input", required=False)
    parser.add_argument('--spend-points', action='store_true', default=False, help="Insert record from user input", required=False)
    parser.add_argument('--run-test', action='store_true', default=False, help="Insert record from user input", required=False)

    args = parser.parse_known_args()[0]
    if args.run_test:
        run_test()
    elif args.delete_all:
        delete_all_records()
    elif args.init_test_data:
        init_test_data()
    elif args.show_balance:
        show_balance()
    elif args.insert_record and args.payer and args.points:
        create_record(args.payer, args.points, args.timestamp)
    elif args.spend_points and args.points:
        spend_points(args.points)
    else:
        print("No operations match your args here. Peace out.")
 
