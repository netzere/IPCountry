from time import time
from flask import Flask, request, jsonify
from app.mongo import IPGeoProviderDAL
from app.vendors import IPGeoVendorsManager, RateLimitExceeded
from app.cache import ClassBCountryCache


app = Flask('App')
app.config['JSON_SORT_KEYS'] = False

vendors_manager = IPGeoVendorsManager()
cache = ClassBCountryCache()


@app.route('/getIPCountry', methods=['GET'])
def get_ip_country():
    try:
        start_time = time()
        ip = request.headers.get('X-Forwarded-For') or request.remote_addr
        cached_country = cache.get_country(ip)

        if cached_country:
            resp = {
                'ip': ip,
                'countryName': cached_country,
            }
        else:
            resp = vendors_manager.get_ip_details(ip)
            cache.set_country(ip, resp['countryName'])

        api_latency = round(1000 * (time() - start_time), 2)
        resp.update({'apiLatency': api_latency})
        return jsonify(resp)
    except RateLimitExceeded:
        return jsonify(error='Rate Limit Exceeded for all vendors'), 429
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        resp = {}
        for vendor in 'ipstack', 'ipapi':
            resp[vendor] = IPGeoProviderDAL.get_vendor_latency_percentiles(vendor)
        return jsonify(resp)
    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
