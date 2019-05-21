import unittest
import os
import datetime

from cdekapi import CdekApi, CdekAPIError


class SimpleTest(unittest.TestCase): 

    @classmethod
    def setUpClass(cls): 
        cls.authLogin = os.environ['CDEK_LOGIN']
        cls.secure = os.environ['CDEK_PASS']
        cls.api = CdekApi(cls.authLogin, cls.secure)

    def test_dict(self): 
        self.assertEqual(self.api.dicts.delivery_types[1], 'дверь-дверь')

    def test_run(self):
        delta = datetime.timedelta(days=1)
        dt = datetime.date.today() + delta
        data = {
            'version':  '1.0',
            'dateExecute':  f'{dt.year}-{dt.month}-{dt.day}',
            'senderCityId':  44,
            'receiverCityId':  137,
            'tariffId':  136,
            'goods':
                [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ],
            'services':  [
                {
                    'id':  2,
                    'param':  3000
                }
            ]
        }
        res = self.api.run('calc', data)
        print(res)
        self.assertEqual(int(res['result']['deliveryPeriodMin']), 1)
        self.assertEqual(res['result']['deliveryDateMin'], (dt + delta).isoformat())
        self.assertEqual(int(res['result']['tariffId']), 136)

    def test_run_failed(self):
        delta = datetime.timedelta(days=1)
        dt = datetime.date.today() + delta
        data = {
            'version': '1.0',
            'dateExecute':  f'{dt.year}-{dt.month}-{dt.day}',
            'senderCityId': '44',
            'receiverCityId': '269',
            'currency': 'RUB',
            'tariffId': 7,
            'goods': 
                [
                    {
                        'weight': '1',
                        'length': '1',
                        'width': '2',
                        'height': '7'
                    }
                ],
        }
        with self.assertRaises(CdekAPIError) as e: 
            self.api.run('calc', data)
        print(e.exception.args[0])
        self.assertEqual(e.exception.args[0]['error'][0]['code'], 3)

    def test_calc(self):
        goods = [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ]
        res = self.api.calc_price(44, 137, goods)
        print(res)
        self.assertEqual(int(res['result']['deliveryPeriodMin']), 1)
        self.assertEqual(int(res['result']['tariffId']), 136)

    def test_calc_num(self):
        goods = [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ]
        res = self.api.calc_price_num(44, 137, goods)
        print(res)
        self.assertGreater(res, 0)

    def test_calc_hr_failed(self):
        goods = [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ]
        with self.assertRaises(CdekAPIError) as e:
            code, res = self.api.calc_price_num(44, 269, goods, tariff_id=7)
        print(e.exception.args[0])
        self.assertEqual(e.exception.args[0]['error'][0]['code'], 3)


if __name__ == '__main__': 
    unittest.main()
