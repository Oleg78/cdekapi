# cdek api
Client for CDEK API
https://confluence.cdek.ru/pages/viewpage.action?pageId=15616129

## Install
0. Read the CDEK manual: https://www.cdek.ru/clients/integrator.html
0. Register new CDEK account
0. Get the access keys via email
0. Clone the repo
0. `pip install .`

## Usage
```python
from cdekapi import CdekApi, CdekAPIError
api = CdekApi(authLogin, secure)
goods = [
            {
                'weight':  0.3,
                'length':  10,
                'width':  7,
                'height':  5
            },
        ]
res = self.api.calc_price(44, 137, goods)
```
