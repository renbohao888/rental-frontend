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

_, r = call('GET', '/dashboard/admin/stats', token=tok_a)
s = r['data']
print('===== 管理员仪表盘 =====')
print('userStats:', s['userStats'])
print('roomStats:', s['roomStats'])
print('orderStats:', s['orderStats'])
print('revenueStats:', s['revenueStats'])
print('recentTrend:', s['recentTrend'])
print('hotRooms:', s['hotRooms'])

_, r = call('GET', '/dashboard/landlord/stats', token=tok_l)
s = r['data']
print()
print('===== 房东仪表盘(官方房东2) =====')
print('totalRooms:', s['totalRooms'], 'published:', s['publishedRooms'], 'rented:', s['rentedRooms'],
      'pendingAudit:', s['pendingAuditRooms'], 'rejected:', s['rejectedRooms'], 'avgRating:', s['avgRating'])
print('totalOrders:', s['totalOrders'], 'activeOrders:', s['activeOrders'], 'thisMonthOrders:', s['thisMonthOrders'],
      'thisMonthRevenue:', s['thisMonthRevenue'], 'avgOrderAmount:', s['avgOrderAmount'])
print('totalRepairs:', s['totalRepairs'], 'pending:', s['pendingRepairs'], 'processing:', s['processingRepairs'])
print('recentOrders:', s['recentOrders'])
