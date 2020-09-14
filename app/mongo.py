import os
import datetime
import numpy

from pymongo import MongoClient


class MongoDBConnection:
    @staticmethod
    def get_collection(collection_name):
        return MongoClient(os.getenv('MONGO_HOST', 'localhost'))['db'][collection_name]


class IPGeoProviderDAL:
    @staticmethod
    def save_request(data):
        request_data = data.copy()
        request_data.update({'timestamp': datetime.datetime.now().timestamp()})
        collection = MongoDBConnection.get_collection('requests')
        collection.insert_one(request_data)

    @staticmethod
    def get_last_hour_request_count_by_ip_and_vendor(ip, vendor):
        collection = MongoDBConnection.get_collection('requests')

        result_set = list(collection.aggregate([{'$match': {'ip': ip, 'vendor': vendor, 'timestamp': {
            '$gte': (datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp()}}},
                                                {'$group': {'_id': '$vendor', 'count': {'$sum': 1}}}]))

        return 0 if not result_set else result_set[0]['count']

    @staticmethod
    def get_vendor_latency_percentiles(vendor):
        collection = MongoDBConnection.get_collection('requests')
        latencies = [item['apiLatency'] for item in
                     collection.aggregate([{'$match': {'vendor': vendor}}, {'$sort': {'apiLatency': 1}}])]

        return {} if not latencies else {
            'percentile50': round(numpy.percentile(latencies, 50), 2),
            'percentile75': round(numpy.percentile(latencies, 75), 2),
            'percentile95': round(numpy.percentile(latencies, 95), 2),
            'percentile99': round(numpy.percentile(latencies, 99), 2),
        }
