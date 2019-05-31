import datetime
import json
from hashlib import md5
import requests
from cdekapi import calc_dictionaries

VERSION = (0, 0, 3)


def get_version():
    return '.'.join(map(str, VERSION))


__version__ = get_version()


class CdekAPIException(Exception):
    pass


class CdekAPIError(CdekAPIException):
    pass


class CdekAPIConnectionError(CdekAPIException):
    pass


class CdekApi:
    """
    Main class
    """
    methods = {
        'calc_price': 'https://api.cdek.ru/calculator/calculate_price_by_json.php',
        'calc_prices': 'http://api.cdek.ru/calculator/calculate_tarifflist.php',
    }
    login = ''
    password = ''
    version = '1.0'
    dicts = calc_dictionaries

    def __init__(self, login=None, password=None):
        """
        Create the api instance
        :param login: cdek login
        :param password: cdek password
        """
        self.login = login
        self.password = password

    def run(self, method, data):
        """
        Query the Yandex API v4
        :param method:
        :param data: json data
        :return: json result
        """
        if data['dateExecute']:
            data['authLogin'] = self.login
            data['secure'] = md5(f"{data['dateExecute']}&{self.password}".encode('utf-8')).hexdigest()

        response = requests.post(self.methods[method], data=json.dumps(data, ensure_ascii=False).encode('utf8'))
        if response.status_code != 200:
            raise CdekAPIConnectionError(response)
        res = response.json()
        if res.get('error', False):
            raise CdekAPIError(res)
        return res

    def calc_price(self,
                   sender_city_id,
                   receiver_city_id,
                   goods,
                   date_execute=None,
                   tariff_id=136,
                   tariff_list=None,
                   mode_id=None,
                   currency='RUB',
                   services=None):

        if not date_execute:
            delta = datetime.timedelta(days=1)
            dt = datetime.date.today() + delta
            date_execute = f'{dt.year}-{dt.month}-{dt.day}'
        else:
            date_execute = f'{date_execute.year}-{date_execute.month}-{date_execute.day}'

        data = {
            'version':  '1.0',
            'dateExecute':  date_execute,
            'senderCityId':  sender_city_id,
            'receiverCityId':  receiver_city_id,
            'goods': goods,
            'currency': currency
        }

        if not tariff_list:
            data['tariffId'] = tariff_id
        else:
            data['tariffList'] = tariff_list

        if services:
            data['services'] = services

        if mode_id:
            data['modeId'] = mode_id

        return self.run('calc_price', data)

    def calc_prices(self,
                    sender_city_id,
                    receiver_city_id,
                    goods,
                    date_execute=None,
                    tariff_id=136,
                    tariff_list=None,
                    mode_id=None,
                    currency='RUB',
                    services=None):

        if not date_execute:
            delta = datetime.timedelta(days=1)
            dt = datetime.date.today() + delta
            date_execute = f'{dt.year}-{dt.month}-{dt.day}'
        else:
            date_execute = f'{date_execute.year}-{date_execute.month}-{date_execute.day}'

        data = {
            'version':  '1.0',
            'dateExecute':  date_execute,
            'senderCityId':  sender_city_id,
            'receiverCityId':  receiver_city_id,
            'goods': goods,
            'currency': currency
        }

        if not tariff_list:
            data['tariffId'] = tariff_id
        else:
            data['tariffList'] = tariff_list

        if services:
            data['services'] = services

        if mode_id:
            data['modeId'] = mode_id

        return self.run('calc_prices', data)

    def calc_price_num(self,
                       sender_city_id,
                       receiver_city_id,
                       goods,
                       date_execute=None,
                       tariff_id=136,
                       tariff_list=None,
                       mode_id=None,
                       currency='RUB',
                       services=None):
        res = self.calc_price(sender_city_id,
                              receiver_city_id,
                              goods,
                              date_execute,
                              tariff_id,
                              tariff_list,
                              mode_id,
                              currency,
                              services)
        return int(res['result']['price'])
