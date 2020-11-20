import requests
from requests.adapters import HTTPAdapter
import json



class HTTP:
    # requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接

    @staticmethod
    def get(url, return_json=True):
        try:
            r = requests.get(url, headers={'connection': 'close'})
            if r.status_code == 200:
                if return_json:
                    return r.json()
                return r.text
            else:
                return {} if return_json else ""
        except requests.ConnectionError as e:
            print(e)
            return {} if return_json else None
