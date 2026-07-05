import urllib.request
import json
try:
    data = json.dumps({'business_type': 'dentist', 'city': 'London', 'country': 'UK', 'radius_meters': 8000, 'enable_website_crawl': True}).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/osm/search', data=data, headers={'Content-Type': 'application/json'})
    r = urllib.request.urlopen(req)
    print(r.read())
except Exception as e:
    if hasattr(e, 'read'):
        print('HTTP Error', e.code, e.read().decode())
    else:
        print('Error:', e)
