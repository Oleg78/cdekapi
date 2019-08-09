import datetime
import json
from hashlib import md5
import requests
import xml.etree.ElementTree as ET

from cdekapi import calc_dictionaries

VERSION = (0, 0, 81)


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
    login = ''
    password = ''
    version = '1.0'
    dicts = calc_dictionaries

    def __init__(self, login=None, password=None, test_mode=False):
        """
        Create the api instance
        :param login: cdek login
        :param password: cdek password
        """
        if test_mode:
            self.login = 'z9GRRu7FxmO53CQ9cFfI6qiy32wpfTkd'
            self.password = 'w24JTCv4MnAcuRTx0oHjHLDtyt3I6IBq'
            self.methods = {
                'calc_price': 'https://api.edu.cdek.ru/calculator/calculate_price_by_json.php',
                'calc_prices': 'https://api.edu.cdek.ru/calculator/calculate_tarifflist.php',
                'pvz_list': 'https://integration.edu.cdek.ru/pvzlist/v1/xml',
                'new_order': 'https://integration.edu.cdek.ru/new_orders.php',
                'status': 'https://integration.edu.cdek.ru/status_report_h.php',
            }
        else:
            self.login = login
            self.password = password
            self.methods = {
                'calc_price': 'https://api.cdek.ru/calculator/calculate_price_by_json.php',
                'calc_prices': 'https://api.cdek.ru/calculator/calculate_tarifflist.php',
                'pvz_list': 'https://integration.cdek.ru/pvzlist/v1/xml',
                'new_order': 'https://integration.cdek.ru/new_orders.php',
                'status': 'https://integration.cdek.ru/status_report_h.php',
            }

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

    def post_xml(self, method, **kwargs):
        """
        Query the CDEK API (POST)
        :param method:
        :param kwargs: POST parameters
        :return: xml result
        """
        data = {}
        for key, val in kwargs.items():
            data[key] = val
        url = f'{self.methods[method]}'
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise CdekAPIConnectionError(response.text)
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

    def new_order(self, order):
        """
        Create new order in cdek
        :param order: dictionary with fields:
            date
            * number
            * sender_city
            * receiver_city
            + tarifftypecode
            * deliveryrecipientcost
            + recepientname
            + recepientemail
            + phone
            * address (one of sets):
                1 street
                1 house
                1 flat
                2 pvzcode
            * packages[]:
                weight
                length
                width
                height
                items[]:
                    * amount
                    * warekey
                    * cost
                    * payment
                    * weight
                    * comment
        :return:
        """
        request = ET.Element('deliveryrequest')
        request.set('account', self.login)
        request.set('secure', self.password)
        request.set('date', order.get('date', str(datetime.date.today()))),
        request.set('number', '1')
        request.set('ordercount', '1')
        request_order = ET.SubElement(request, 'order')
        request_order.set('number', str(order['number']))
        request_order.set('sendcitycode', str(order['sender_city']))
        request_order.set('reccitycode', str(order['receiver_city']))
        request_order.set('tarifftypecode', str(order['tarifftypecode']))
        request_order.set('deliveryrecipientcost',
                          str(order['deliveryrecipientcost']) if order['deliveryrecipientcost'] else 0)
        request_order.set('recipientname', str(order['recipientname']))
        request_order.set('recepientemail', str(order['recepientemail']))
        request_order.set('phone', str(order['phone']))
        address = ET.SubElement(request_order, 'address')
        if order['address'].get('street'):
            address.set('street', order['address'].get('street'))
        if order['address'].get('house'):
            address.set('house', str(order['address'].get('house')))
        if order['address'].get('flat'):
            address.set('flat', str(order['address'].get('flat')))
        if order['address'].get('pvzcode'):
            address.set('pvzcode', order['address'].get('pvzcode'))
        package_number = 1
        for order_package in order['packages']:
            package = ET.SubElement(request_order, 'package')
            package.set('number', str(package_number))
            package.set('barcode', str(package_number))
            package_number += 1
            package.set('weight', str(order_package['weight']))
            package.set('sizea', str(order_package['height']))
            package.set('sizeb', str(order_package['width']))
            package.set('sizec', str(order_package['length']))
            for package_item in order_package['items']:
                item = ET.SubElement(package, 'item')
                item.set('amount', str(package_item['amount']))
                item.set('warekey', package_item['warekey'])
                item.set('cost', str(package_item['cost']))
                item.set('payment', str(package_item['payment']))
                item.set('weight', str(package_item['weight']))
                item.set('comment', package_item['comment'])
        data = ET.tostring(request, encoding='utf-8')
        res = self.post_xml('new_order', xml_request=data)
        root = ET.fromstring(res)
        if root[0].get('ErrorCode'):
            raise CdekAPIError(root[0].get('Msg'))
        dispatch_number = root[0].get('DispatchNumber')
        order_number = root[0].get('Number')
        return order_number, dispatch_number

    def check_orders_status(self, orders):
        """
        Check orders status
        :param orders: list of orders
            {
                order_number,
                dispatch_number
            }
        :return: list of orders with statuses
        """
        request = ET.Element('statusreport')
        request.set('account', self.login)
        request.set('secure', self.password)
        request.set('date', str(datetime.date.today())),
        for order in orders:
            request_order = ET.SubElement(request, 'order')
            request_order.set('number', str(order['order_number']))
            request_order.set('dispatch_number', str(order['dispatch_number']))
        data = ET.tostring(request, encoding='utf-8')
        res = self.post_xml('status', xml_request=data)
        root = ET.fromstring(res)
        if root.get('ErrorCode'):
            raise CdekAPIError(root.get('Msg'))
        ET.dump(root)
        for order in root:
            print('ORDER', order.attrib['Number'], order.attrib['DispatchNumber'])
            status = order.find('Status')
            print('STATUS', status.attrib['Date'], status.attrib['Code'], status.attrib['Description'])
        return root