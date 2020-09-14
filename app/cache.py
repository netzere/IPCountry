import os
import redis


class IPClassBInfo:
    def __init__(self, ip):
        self.octet_1, self.octet_2, _, _ = ip.split('.')

    def ip_in_class_b(self):
        return 128 <= int(self.octet_1) <= 191 and 0 <= int(self.octet_2) <= 255

    def get_ip_prefix(self):
        return f'{self.octet_1}.{self.octet_2}'


class ClassBCountryCache:
    def __init__(self):
        self.redis = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'),
                                       charset='utf-8', decode_responses=True)

    def set_country(self, ip, country_name):
        ip_info = IPClassBInfo(ip)

        if ip_info.ip_in_class_b():
            ip_prefix = ip_info.get_ip_prefix()
            self.redis.set(ip_prefix, country_name)

    def get_country(self, ip):
        ip_info = IPClassBInfo(ip)
        ip_prefix = ip_info.get_ip_prefix()

        return self.redis.get(ip_prefix)
