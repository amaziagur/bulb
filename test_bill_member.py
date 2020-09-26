import unittest
from unittest.mock import patch
import bill_member
from utils import TariffComputer


class TestBillMember(unittest.TestCase):

    def test_calculate_bill_for_august(self):
        amount, kwh = bill_member.calculate_bill(member_id='member-123',
                                  account_id='ALL',
                                  bill_date='2017-08-31')
        self.assertEqual(int(amount), int(27.57))
        self.assertEqual(round(kwh), 167)

    @patch('load_readings.get_readings')
    def test_compute_bill_for_no_readings(self, get_readings):
        get_readings.return_value = {"member-123": [{"account-abc": [{"electricity": []}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='electricity', bill_date='2017-08-31')
        expected_amount = TariffComputer().metric('electricity').compute(0, 0)
        self.assert_that(bill_content={amount: expected_amount, kwh: 0})

    def assert_that(self, bill_content):
        for k,v in bill_content.items():
            self.assertEqual(k, v)
            self.assertEqual(k, v)

    @patch('load_readings.get_readings')
    def test_compute_bill_for_first_month(self, get_readings):
        cumulative = 101
        days = 31
        get_readings.return_value = {"member-123": [{"account-abc": [{"electricity": [{"cumulative": cumulative, "readingDate": "2017-03-31T00:00:00.000Z", "unit": "kWh"}]}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='electricity', bill_date='2017-03-31')
        expected_amount = TariffComputer().metric('electricity').compute(cumulative, days)
        self.assert_that(bill_content={int(amount): int(expected_amount), int(kwh): cumulative})

    @patch('load_readings.get_readings')
    def test_compute_bill_for_two_months(self, get_readings):
        cumulative = 250
        days = 31
        get_readings.return_value = {"member-123": [{"account-abc": [{"electricity": [{"cumulative": 101, "readingDate": "2017-07-31T00:00:00.000Z", "unit": "kWh"},
                                                                                      {"cumulative": 351, "readingDate": "2017-08-31T00:00:00.000Z", "unit": "kWh"}]}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='electricity', bill_date='2017-08-31')
        expected_amount = TariffComputer().metric('electricity').compute(cumulative, days)
        self.assert_that(bill_content={int(amount): int(expected_amount), int(round(kwh)): cumulative})

    @patch('load_readings.get_readings')
    def test_retrieve_bill_given_no_upper_bound_reading(self, get_readings):
        get_readings.return_value = {"member-123": [{"account-abc": [{"electricity": [{"cumulative": 101, "readingDate": "2017-07-05T00:00:00.000Z", "unit": "kWh"}, {"cumulative": 351, "readingDate": "2017-08-16T00:00:00.000Z", "unit": "kWh"}]}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='electricity', bill_date='2017-08-31')
        expected_amount = TariffComputer().metric('electricity').compute(95.23, 31)
        self.assert_that(bill_content={int(amount): int(expected_amount), int(kwh): int(95.23)})

    @patch('load_readings.get_readings')
    def test_between_years(self, get_readings):
        get_readings.return_value = {
                                                            "member-123": [{
                                                                "account-abc": [{
                                                                    "electricity": [
                                                                        {
                                                                          "cumulative": 19150,
                                                                          "readingDate": "2017-11-04T00:00:00.000Z",
                                                                          "unit": "kWh"
                                                                        },
                                                                        {
                                                                            "cumulative": 19517,
                                                                            "readingDate": "2017-12-31T00:00:00.000Z",
                                                                            "unit": "kWh"
                                                                        },
                                                                        {
                                                                            "cumulative": 19757,
                                                                            "readingDate": "2018-01-23T00:00:00.000Z",
                                                                            "unit": "kWh"
                                                                        }
                                                                    ]
                                                                }]
                                                            }]
                                                        }
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='electricity', bill_date='2018-01-31')
        expected_amount = TariffComputer().metric('electricity').compute(240, 31)
        self.assert_that(bill_content={int(amount): int(expected_amount), int(kwh): int(240)})

    @patch('load_readings.get_readings')
    def test_compute_gas_bill_for_two_months(self, get_readings):
        cumulative = 250
        days = 31
        get_readings.return_value = {"member-123": [{"account-abc": [{"gas": [
            {"cumulative": 101, "readingDate": "2017-07-31T00:00:00.000Z", "unit": "kWh"},
            {"cumulative": 351, "readingDate": "2017-08-31T00:00:00.000Z", "unit": "kWh"}
        ]}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='gas', bill_date='2017-08-31')
        expected_amount = TariffComputer().metric('gas').compute(cumulative, days)
        self.assert_that(bill_content={int(amount): int(expected_amount), int(round(kwh)): cumulative})

    @patch('load_readings.get_readings')
    def test_compute_gas_and_electricity_bill_for_two_months(self, get_readings):
        cumulative = 250
        days = 31
        get_readings.return_value = {"member-123":[{"account-abc":[
            {"electricity":[{"cumulative":101,"readingDate":"2017-07-31T00:00:00.000Z","unit":"kWh"},{"cumulative":351,"readingDate":"2017-08-31T00:00:00.000Z","unit":"kWh"}]},
            {"gas":[{"cumulative":101,"readingDate":"2017-07-31T00:00:00.000Z","unit":"kWh"},{"cumulative":351,"readingDate":"2017-08-31T00:00:00.000Z","unit":"kWh"}]}]}]}
        amount, kwh = bill_member.calculate_bill(member_id='member-123', account_id='ALL', bill_date='2017-08-31')
        electricity = TariffComputer().metric('electricity').compute(cumulative, days)
        gas = TariffComputer().metric('gas').compute(cumulative, days)
        self.assert_that(bill_content={int(amount): int(electricity+gas), int(round(kwh)): 500})



if __name__ == '__main__':
    unittest.main()
