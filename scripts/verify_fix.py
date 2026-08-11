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

def login(acc, pwd):
    _, r = call('POST', '/user/login', {'accountNo': acc, 'password': pwd})
    return r['data']['token']

tok_a = login('10000000', '123456')
tok_l = login('88888888', '123456')

# 1. 房东列表（管理员）
_, r = call('GET', '/user/admin/list?pageNum=1&pageSize=10&role=1', token=tok_a)
print('===== 管理员-房东列表 role=1 =====')
print('total:', r['total'])
for u in r['records']:
    print('  id=%s nickname=%s accountNo=%s phone=%s auditStatus=%s' % (u['id'], u['nickname'], u['accountNo'], u['phone'], u['auditStatus']))

# 2. 按房东过滤房源（管理员）
_, r = call('GET', '/room/admin/list?pageNum=1&pageSize=2&landlordId=2', token=tok_a)
print()
print('===== 管理员-房东2的房源过滤 =====')
print('code:', r['code'], 'total:', r['data']['total'])
for room in r['data']['records']:
    print('  id=%s title=%s landlordId=%s' % (room['id'], room['title'], room['landlordId']))

_, r = call('GET', '/room/admin/list?pageNum=1&pageSize=2&landlordId=5', token=tok_a)
print('landlordId=5 total:', r['data']['total'])

# 3. 房东个人中心数据（真实用户信息）
_, r = call('GET', '/user/info', token=tok_l)
print()
print('===== 房东个人中心 /user/info =====')
print('code:', r['code'])
print('  accountNo:', r['data']['accountNo'], 'nickname:', r['data']['nickname'],
      'phone:', r['data']['phone'], 'avatar:', r['data'].get('avatar'),
      'isVerified:', r['data'].get('isVerified'), 'email:', r['data'].get('email'))

# 4. 仪表盘仍正常
_, r = call('GET', '/dashboard/admin/stats', token=tok_a)
print()
print('===== 管理员仪表盘（回归） =====')
print('code:', r['code'], 'landlordCount:', r['data']['userStats']['landlordCount'], 'totalRooms:', r['data']['roomStats']['totalRooms'])
