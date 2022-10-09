import transactionSender
import unittest


class TestTransactionSender(unittest.TestCase):
    def setUp(self):
        self.test_data = [{ "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" },
            { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" },
            { "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" },
            { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" },
            { "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }
            ]

    def tearDown(self):
        transactionSender.delete_all_records()

    def test_init_test_data(self):
        resp = transactionSender.init_test_data(self.test_data)
        self.assertTrue(resp['StatusCode'] == 200)

    def test_sequece_op(self):
        resp = transactionSender.init_test_data(self.test_data)
        self.assertEqual(resp['StatusCode'], 200)
        resp = transactionSender.spend_points(5000)
        expect_result = [{'payer': 'DANNON', 'points': -100}, {'payer': 'UNILEVER', 'points': -200}, {'payer': 'MILLER COORS', 'points': -4700}]
        self.assertEqual(resp, expect_result)
        resp = transactionSender.show_balance()
        expect_balance = { "UNILEVER": 0, "MILLER COORS": 5300, "DANNON": 1000}
        self.assertEqual(resp, expect_balance)

if __name__ == '__main__':
    unittest.main()

