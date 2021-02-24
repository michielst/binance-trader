import requests


class Api:
    def get(self, url, params):
        return requests.get(url, headers=(()), params=params).json()
