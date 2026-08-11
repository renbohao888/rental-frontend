# -*- coding: utf-8 -*-
"""验证管理员轮播图功能 + 用户信息补全 + 仪表盘回归"""
import urllib.request, json, urllib.error

BASE = 'http://localhost:5173/api'

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

# 管理员登录
_, r = call('POST', '/user/login', {'accountNo': '10000000', 'password': '123456'})
tok = r['data']['token']
print('admin login ok')

# 1. 管理员轮播图列表
_, r = call('GET', '/banner/admin/list?pageNum=1&pageSize=10', token=tok)
print('===== 管理员轮播图列表 =====')
print('code:', r['code'], 'total:', r['data']['total'])
for b in r['data']['records']:
    print('  id=%s title=%s status=%s' % (b['id'], b['title'], b['status']))

# 2. 新增一条轮播图
_, r = call('POST', '/banner/admin/add',
            {'title': '测试轮播图', 'imageUrl': '/uploads/image/2026-08/1786386328194_35820091.jpg',
             'linkUrl': '', 'sortOrder': 9, 'status': 1}, token=tok)
print('===== 新增轮播图 =====')
print('code:', r['code'], r['message'])

# 3. 更新它（禁用）
_, r = call('GET', '/banner/admin/list?pageNum=1&pageSize=20', token=tok)
test_b = [b for b in r['data']['records'] if b['title'] == '测试轮播图'][0]
_, r = call('PUT', '/banner/admin/update', {'id': test_b['id'], 'status': 0, 'title': '测试轮播图已禁用'}, token=tok)
print('===== 更新轮播图(禁用) =====')
print('code:', r['code'], r['message'])

# 4. 删除它
_, r = call('DELETE', '/banner/admin/%s' % test_b['id'], token=tok)
print('===== 删除轮播图 =====')
print('code:', r['code'], r['message'])

# 5. 公开列表应仍为 5 条
_, r = call('GET', '/banner/list')
print('===== 公开轮播图列表 =====')
print('code:', r['code'], 'count:', len(r['data']))

# 6. 用户信息补全核对
_, r = call('POST', '/user/login', {'accountNo': '88888888', 'password': '123456'})
tokl = r['data']['token']
_, r = call('GET', '/user/info', token=tokl)
u = r['data']
print('===== 房东 /user/info =====')
print('account:', u['accountNo'], 'nickname:', u['nickname'], 'phone:', u['phone'])

# 7. 仪表盘回归
_, r = call('GET', '/dashboard/admin/stats', token=tok)
d = r['data']
print('===== 管理员仪表盘 =====')
print('landlordCount:', d['userStats']['landlordCount'], 'totalRooms:', d['roomStats']['totalRooms'])
