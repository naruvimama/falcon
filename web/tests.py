import requests
import pytest
import json
import time


BASE_URL    = 'http://localhost:8000'

def test_add_endpoint():
    response = requests.post(BASE_URL + '/add', data = 'Some data')
    actual = json.loads(response.content.decode('ascii'))
    assert actual.get('topic', None) == 'json_msgs'
    assert actual.get('partition', None) == 0

def test_get_all_endpoint():
    response = requests.post(BASE_URL + '/add', data = 'Some data')
    response = requests.post(BASE_URL + '/add', data = 'Some data')

    response = requests.get(BASE_URL + '/get_all?limit=3', stream=True)
    response.encoding = 'utf-8'
    actual = []

    for line in response.iter_lines(decode_unicode=True):
        if line:
            print(line)
            actual.append(line)
    assert actual

if __name__=='__main__':
    #test_add_endpoint()
    test_get_all_endpoint()
