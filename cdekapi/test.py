import unittest
import datetime
import xml.etree.ElementTree as ET
import uuid

from cdekapi import CdekApi, CdekAPIError


class PostTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = CdekApi(test_mode=True)

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
        res = self.api.run('calc_price', data)
        print(res)
        self.assertEqual(int(res['result']['deliveryPeriodMin']), 1)
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
            self.api.run('calc_price', data)
        print(e.exception.args[0])
        self.assertEqual(e.exception.args[0]['error'][0]['code'], 3)

    def test_calc_price(self):
        goods = [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ]
        tariffs = [
            {'id': 136, 'priority': 1},
            {'id': 137, 'priority': 2},
            {'id': 233, 'priority': 3},
            {'id': 234, 'priority': 4},
            {'id': 291, 'priority': 5},
            {'id': 294, 'priority': 6}
        ]
        res = self.api.calc_price(44, 137, goods, tariff_list=tariffs)
        print(res)
        self.assertEqual(int(res['result']['deliveryPeriodMin']), 1)
        self.assertEqual(int(res['result']['tariffId']), 136)

    def test_calc_price_round(self):
        goods = [
            {
                'weight': 0.3,
                'length': 10,
                'width': 7,
                'height': 5
            },
        ]
        tariffs = [
            {'id': 136, 'priority': 1},
            {'id': 137, 'priority': 2},
            {'id': 233, 'priority': 3},
            {'id': 234, 'priority': 4},
            {'id': 291, 'priority': 5},
            {'id': 294, 'priority': 6}
        ]
        services = [
            {
                'id': 2,
                'param': 3000
            }
        ]
        res = self.api.calc_price(44, 137, goods, tariff_list=tariffs, services=services)
        res2 = self.api.calc_price(44, 137, goods, tariff_list=tariffs, services=services, decimal_places=2)
        print(res)
        print(res2)
        self.assertEqual(res['result']['price'], round(res['result']['price'], 2))

    def test_calc_prices(self):
        goods = [
                    {
                        'weight':  0.3,
                        'length':  10,
                        'width':  7,
                        'height':  5
                    },
                ]
        tariffs = [
            {'id': 136},
            {'id': 137},
            {'id': 233},
            {'id': 234},
            {'id': 291},
            {'id': 294},
            {'id': 59},
            {'id': 11},
        ]
        res = self.api.calc_prices(44, 137, goods, tariff_list=tariffs)
        print(res)
        self.assertEqual(int(res['result'][0]['status']), True)
        self.assertEqual(int(res['result'][4]['status']), False)

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


class GetXmlTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = CdekApi(test_mode=True)

    def test_get_xml(self):
        res = self.api.get_xml('pvz_list', cityid=270, allowedcod=1)
        print(res)
        root = ET.fromstring(res)
        self.assertEqual(root.tag, 'PvzList')

    def test_get_pvz_list(self):
        res = self.api.get_pvz_list(270, 1)
        print(res)
        self.assertEqual(res[0]['name'], 'Академгородок')


class OrderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = CdekApi(test_mode=True)

    def test_new_order(self):
        order_no = str(uuid.uuid4())
        order = {
            'number': order_no,
            'sender_city': 44,
            'receiver_city': 137,
            'tarifftypecode': 136,
            'recipientname': 'Иванов Андрей Петрович',
            'recepientemail': 'a@a.ru',
            'phone': '5566656595',
            'address': {
                'pvzcode': 'SPB11'
            },
            'packages': [
                {
                    'weight': 100,
                    'length': 40,
                    'width': 30,
                    'height': 30,
                    'items': [
                        {
                            'amount': 1,
                            'warekey': 'АРТ',
                            'cost': 1000,
                            'payment': 0,
                            'weight': 100,
                            'comment': 'no comment'
                        }
                    ]
                }
            ]
        }
        order_number, dispatch_number = self.api.new_order(order=order)
        self.assertEqual(order_number, order_no)


if __name__ == '__main__': 
    unittest.main()
