import os
import requests

from .mongo import IPGeoProviderDAL

IPSTACK_API_ENDPOINT = 'http://api.ipstack.com'
IPAPI_API_ENDPOINT = 'http://api.ipapi.com'


class RateLimitExceeded(Exception):
    pass


class IPGeoVendor:
    """
        I used the same class for both providers.
        I wouldn't really do this, it was just to save time because they have the same API
    """
    def __init__(self, name, url, access_key, rate_limit_per_hour):
        self.name = name
        self.url = url
        self.access_key = access_key
        self.rate_limit_per_hour = rate_limit_per_hour

    def _rate_limited(self, ip):
        return IPGeoProviderDAL.get_last_hour_request_count_by_ip_and_vendor(ip, self.name) >= self.rate_limit_per_hour

    def get_ip_details(self, ip):
        if self._rate_limited(ip):
            raise RateLimitExceeded

        vendor_resp = requests.get(f'{self.url}/{ip}', params={'access_key': self.access_key}, timeout=2)

        if vendor_resp.status_code == 429:
            raise RateLimitExceeded

        country_name = vendor_resp.json()['country_name']
        IPGeoProviderDAL.save_request({
            'ip': ip,
            'apiLatency': round(vendor_resp.elapsed.microseconds / 1000, 2),
            'vendor': self.name
        })  # we don't save the country name in mongo, since we don't use it

        return {
            'ip': ip,
            'vendor': self.name,
            'countryName': country_name
        }


class IPGeoVendorsManager:
    def __init__(self):
        self.primary = IPGeoVendor(name='ipstack', url=IPSTACK_API_ENDPOINT,
                                   access_key=os.getenv('IPSTACK_ACCESS_KEY'),
                                   rate_limit_per_hour=int(os.getenv('IPSTACK_MAX_REQUESTS_PER_USER_PER_HOUR', 2)))
        self.secondary = IPGeoVendor(name='ipapi', url=IPAPI_API_ENDPOINT,
                                     access_key=os.getenv('IPSTACK_ACCESS_KEY'),
                                     rate_limit_per_hour=int(os.getenv('IPAPI_MAX_REQUESTS_PER_USER_PER_HOUR', 2)))

    def _fallback(self, ip_addr):
        return self.secondary.get_ip_details(ip_addr)

    def get_ip_details(self, ip_addr):
        try:
            return self.primary.get_ip_details(ip_addr)
        except RateLimitExceeded:
            return self._fallback(ip_addr)
