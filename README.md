# TransactionService

## Introduction
Each user can spend points and there are other payers will pay for the points.

---

## System settings
- Client side application: command line interface `transactionSender.py`
- Server side service: AWS lambda serverless service `lambda_function.py`. Throttled by 2 concurrent API call at a time.
- Database setting: AWS DynamoDB
- Database records: `{'payer': String [Partition Key], 'timestamp': String [Sort Key], 'points': Decimal}`. The Primary Key consists of Sort key and Partition key.

---

## Requirements
- python 3.x
- git

---

## Installation
1. `git clone git@github.com:YaoChungLiang/TransactionService.git`

---

## Usage
- Run unit tests to check the functions all pass the the tests
    
    1. `cd TransactionService/src/client_cli`
    2. `python3 test_transactionSender.py`
    3. All the tests should pass
- Use command line interface script to send requests to the AWS lambda service and modify the records in the database. 

    1. Run `python3 transactionSender.py --init-test-data` initialize the test data
    2. Run `python3 transactionSender.py --spend-points --points 5000` to spend 5000 points
    3. Run `python3 transactionSender.py --show-balance` to show the final balance
    4. Run `python3 transactionSender.py --delete-all` to delete all the records in the database.
    5. Run `python3 transactionSender.py --insert-record --payer DEBO --points 300` to insert a record in the database.
- Create your own lambda service and DynamoDB database
    1. Create a DynamoDb Table call `Transaction` follow by the [instrunctions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
    2. Create a lambda function and give the lambda function permission to access the DynamoDB you created follow the [instrunctions](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)
    3. `cd TransactionService/src/backend`
    4. Packaging the lambda function by `bash builder.bash entrypoint`
    5. Upload the tarball `entrypoint.zip` to the lambda function you created.
    6. The service is up.
