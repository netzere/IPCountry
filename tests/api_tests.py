import random
import requests


def get_ip(class_b=False):
    if class_b:
        return '.'.join(map(str, (random.randint(128, 191) for _ in range(4))))
    else:
        return '.'.join(map(str, (random.randint(0, 127) for _ in range(4))))


def test_class_b_ips():

    for _ in range(3):
        print('Running tests against classB IP.. Expecting to see the cache in action..')
        print('First call, expecting to see a call to the vendor..')
        ip = get_ip(class_b=True)
        test(ip)
        print('subsequent calls, expecting to see the cache in action...')
        for _ in range(3):
            test(ip)

        print('=' * 120 + '\n' + '=' * 120)


def test_non_class_b_ips():
    for _ in range(3):
        print(
            'Running tests against non classB IP.. Expecting to see the vendor fallback and the rate limit in action..')
        ip = get_ip()
        for _ in range(5):
            test(ip)
        print('=' * 120 + '\n' + '=' * 120)


def test(ip):
    print(requests.get('http://localhost:8000/getIPCountry', headers={'X-Forwarded-For': ip}).json())


if __name__ == '__main__':
    test_class_b_ips()
    test_non_class_b_ips()
