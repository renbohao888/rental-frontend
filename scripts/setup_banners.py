# -*- coding: utf-8 -*-
"""1) 补全缺失的用户手机号  2) 上传美女图片  3) 插入轮播图数据"""
import pymysql
import json
import urllib.request
import urllib.error
import uuid
import os

BASE = 'http://localhost:8080/api'
IMG_DIR = r'D:\work\rental-frontend\scripts\img'


def call(method, path, payload=None, token=None, files=None):
    """支持 JSON 或 multipart"""
    headers = {}
    data = None
    if files:
        boundary = uuid.uuid4().hex
        body = b''
        for name, (fname, content, ctype) in files.items():
            body += ('--%s\r\n' % boundary).encode()
            body += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (name, fname)).encode()
            body += ('Content-Type: %s\r\n\r\n' % ctype).encode()
            body += content + b'\r\n'
        body += ('--%s--\r\n' % boundary).encode()
        data = body
        headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary
    elif payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    if token:
        req.add_header('Authorization', token)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))


# ============ 1. 补全用户手机号 ============
conn = pymysql.connect(host='localhost', port=3306, user='root', password='1232731qW',
                       database='room_rent_db', charset='utf8mb4')
cur = conn.cursor()
phone_map = {1: '13800000001', 2: '13800000100', 3: '13800000003'}
for uid, phone in phone_map.items():
    cur.execute('UPDATE user SET phone=%s WHERE id=%s AND (phone IS NULL OR phone="")', (phone, uid))
conn.commit()
cur.execute('SELECT id, account_no, nickname, phone FROM user ORDER BY id')
print('===== 补全后的用户手机号 =====')
for r in cur.fetchall():
    print('id=%s account=%s nickname=%s phone=%s' % r)

# ============ 2. 登录管理员获取 token ============
_, r = call('POST', '/user/login', {'accountNo': '10000000', 'password': '123456'})
tok = r['data']['token']
print('admin token ok')

# ============ 3. 上传图片并获取 URL ============
banners = [
    ('u1', '遇见心动小屋 · 精选房源', '1'),
    ('u2', '品质生活 · 拎包入住', '2'),
    ('u3', '新客专享 · 首单立减', '3'),
    ('u4', '海量好房 · 一键优选', '4'),
    ('u5', '舒适安家 · 安心租住', '5'),
]
urls = {}
for fname, _t, _s in banners:
    path = os.path.join(IMG_DIR, fname + '.jpg')
    with open(path, 'rb') as f:
        content = f.read()
    code, r = call('POST', '/upload/image', token=tok,
                   files={'file': (fname + '.jpg', content, 'image/jpeg')})
    if code == 200 and r.get('code') == 200:
        urls[fname] = r['data']
        print('%s uploaded -> %s' % (fname, r['data']))
    else:
        print('%s upload FAILED: %s %s' % (fname, code, r))

# ============ 4. 插入轮播图 ============
cur.execute('DELETE FROM banner')
import time, random
snow = int(time.time() * 1000) << 22
for fname, title, sort_order in banners:
    if fname in urls:
        # 后端 IdType.ASSIGN_ID 使用雪花算法，这里模拟生成唯一 long id
        snow += 1
        # 将上传返回的 /C:/...uploads/... 转为可访问的 /uploads/... 相对路径
        rel = urls[fname]
        if 'uploads/' in rel:
            rel = '/uploads/' + rel.split('uploads/', 1)[1]
        cur.execute(
            'INSERT INTO banner (id, title, image_url, link_url, sort_order, status) VALUES (%s,%s,%s,%s,%s,1)',
            (snow, title, rel, '', int(sort_order))
        )
conn.commit()
cur.execute('SELECT id, title, image_url, sort_order, status FROM banner ORDER BY sort_order')
print('===== 轮播图列表 =====')
for r in cur.fetchall():
    print(r)
conn.close()
print('done')
