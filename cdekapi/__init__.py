import datetime
import json
from hashlib import md5
import requests
import xml.etree.ElementTree as ET

from cdekapi import calc_dictionaries

VERSION = (0, 0, 5)


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
        'pvz_list': 'http://integration.cdek.ru/pvzlist/v1/xml'
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
        Query the CDEK API (POST)
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

    def get_xml(self, method, **kwargs):
        """
        Query the CDEK API (GET)
        :param method:
        :param kwargs: GET parameters
        :return: xml result
        """
        q = ''
        for key, val in kwargs.items():
            q += '&' if q > '' else ''
            q += f'{key}={val}'
        url = f'{self.methods[method]}?{q}'
        response = requests.get(url)
        if response.status_code != 200:
            raise CdekAPIConnectionError(response)
        return response.text

    def calc_price(self,
                   sender_city_id,
                   receiver_city_id,
                   goods,
                   date_execute=None,
                   tariff_id=136,
                   tariff_list=None,
                   mode_id=None,
                   currency='RUB',
                   services=None,
                   decimal_places=0):

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

        res = self.run('calc_price', data)
        res['result']['price'] = round(float(res['result']['price']), decimal_places)

        return res

    def calc_prices(self,
                    sender_city_id,
                    receiver_city_id,
                    goods,
                    date_execute=None,
                    tariff_id=136,
                    tariff_list=None,
                    mode_id=None,
                    currency='RUB',
                    services=None,
                    decimal_places=0):

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

        res = self.run('calc_prices', data)
        for r in res['result']:
            if r['status']:
                r['result']['price'] = round(float(r['result']['price']), decimal_places)

        return res

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

    def get_pvz_list(self, city_id, np_allowed):
        """
        Get the list of pvz for a city
        :param city_id: CDEK City Id
        :param np_allowed: 1/0
        :return: dict of pvz
        """
        res = self.get_xml('pvz_list', cityid=city_id, allowedcod=np_allowed)
        root = ET.fromstring(res)
        pvz_list = []
        for pvz in root:
            pvz_list.append({
                'id': pvz.attrib.get('Code'),
                'name': pvz.attrib.get('Name'),
                'city': pvz.attrib.get('City'),
                'address': pvz.attrib.get('Address'),
                'comment': pvz.attrib.get('AddressComment'),
                'note': pvz.attrib.get('Note'),
                'phone': pvz.attrib.get('Phone'),
                'latitude': pvz.attrib.get('coordX'),
                'longitude': pvz.attrib.get('coodrY'),
                'type': pvz.attrib.get('Type'),
                'np_allowed': pvz.attrib.get('AllowedCod'),
            })
        return pvz_list
