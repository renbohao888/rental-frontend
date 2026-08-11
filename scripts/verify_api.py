# -*- coding: utf-8 -*-
import urllib.request, json, urllib.error

BASE = 'http://localhost:8080/api'

def call(method, path, payload=None, token=None):
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={'Content-Type': 'application/json'})
    if token:
        req.add_header('Authorization', token)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

# 租客 49 登录
_, r = call('POST', '/user/login', {'accountNo': '2086868249202528256', 'password': 'Test1234'})
tok_t = r['data']['token']
code, r = call('GET', '/room/recommend?limit=8', token=tok_t)
print('tenant /room/recommend -> code:', code, 'rooms:', len(r['data']) if r['data'] else 0)
if r['data']:
    for x in r['data'][:2]:
        print('   -', x['id'], x['title'], x['price'])

# 房东 2 登录
_, r = call('POST', '/user/login', {'accountNo': '88888888', 'password': '123456'})
tok_l = r['data']['token']
code, r = call('GET', '/room/my?pageNum=1&pageSize=5', token=tok_l)
print('landlord /room/my -> http:', code, 'body:', json.dumps(r, ensure_ascii=False)[:200])
if isinstance(r, dict) and r.get('data') and isinstance(r['data'], dict):
    print('   total:', r['data'].get('total'))

# 管理员 1 登录
_, r = call('POST', '/user/login', {'accountNo': '10000000', 'password': '123456'})
tok_a = r['data']['token']
code, r = call('GET', '/room/admin/list?pageNum=1&pageSize=3', token=tok_a)
print('admin /room/admin/list -> code:', code, 'total:', r['data']['total'] if isinstance(r, dict) and r.get('data') and isinstance(r['data'], dict) else 'n/a')

# 游客列表
code, r = call('GET', '/room/list?pageNum=1&pageSize=3')
print('public /room/list -> code:', code, 'total:', r['data']['total'] if isinstance(r, dict) and r.get('data') else 'n/a')
