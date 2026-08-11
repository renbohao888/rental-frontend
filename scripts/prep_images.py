# -*- coding: utf-8 -*-
"""查询所有用户信息 + 测试下载美女图片"""
import pymysql
import urllib.request

conn = pymysql.connect(host='localhost', port=3306, user='root', password='1232731qW',
                       database='room_rent_db', charset='utf8mb4')
cur = conn.cursor()
cur.execute('SELECT id, account_no, nickname, role, phone, audit_status FROM user ORDER BY id')
print('===== 用户列表 =====')
for r in cur.fetchall():
    print('id=%s account=%s nickname=%s role=%s phone=%r audit_status=%s' % r)
conn.close()

print()
print('===== 测试下载美女图片 =====')
urls = {
    'u1': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=1200&h=400&fit=crop&crop=faces&q=80',
    'u2': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=1200&h=400&fit=crop&crop=faces&q=80',
    'u3': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1200&h=400&fit=crop&crop=faces&q=80',
    'u4': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=1200&h=400&fit=crop&crop=faces&q=80',
    'u5': 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=1200&h=400&fit=crop&crop=faces&q=80',
}
import os
os.makedirs(r'D:\work\rental-frontend\scripts\img', exist_ok=True)
for name, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
        with open(r'D:\work\rental-frontend\scripts\img\%s.jpg' % name, 'wb') as f:
            f.write(data)
        print('%s OK bytes=%d' % (name, len(data)))
    except Exception as e:
        print('%s FAIL %s' % (name, e))
