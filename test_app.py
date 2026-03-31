import requests

BASE = 'http://localhost:8000'


def test_root():
    r = requests.get(f'{BASE}/')
    assert r.status_code == 200


def test_portal_index():
    r = requests.get(f'{BASE}/portal/')
    assert r.status_code == 200
    assert 'VibeShop Seller Portal' in r.text
