# -*- coding: utf-8 -*-
"""清理验证残留的测试轮播图"""
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='1232731qW',
                       database='room_rent_db', charset='utf8mb4')
cur = conn.cursor()
cur.execute("DELETE FROM banner WHERE title IN ('测试轮播图已禁用', '测试轮播图')")
conn.commit()
cur.execute('SELECT id, title, sort_order, status FROM banner ORDER BY sort_order')
for r in cur.fetchall():
    print(r)
conn.close()
