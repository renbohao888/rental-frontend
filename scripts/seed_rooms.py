# -*- coding: utf-8 -*-
"""
生成 100 条房源测试数据并插入 room 表
用法: python seed_rooms.py
"""
import random
import datetime
import pymysql

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='1232731qW',
    database='room_rent_db', charset='utf8mb4'
)
cur = conn.cursor()
random.seed(20260811)

CITIES = [
    ('北京', 39.9042, 116.4074, ['朝阳', '海淀', '丰台', '西城', '东城', '通州', '昌平']),
    ('上海', 31.2304, 121.4737, ['徐汇', '静安', '浦东', '长宁', '虹口', '杨浦', '普陀']),
    ('广州', 23.1291, 113.2644, ['天河', '越秀', '海珠', '荔湾', '白云', '番禺', '黄埔']),
    ('深圳', 22.5431, 114.0579, ['福田', '南山', '罗湖', '宝安', '龙岗', '龙华', '盐田']),
    ('杭州', 30.2741, 120.1551, ['西湖', '拱墅', '滨江', '上城', '余杭', '萧山']),
    ('成都', 30.5728, 104.0668, ['锦江', '武侯', '青羊', '金牛', '成华', '高新']),
    ('武汉', 30.5928, 114.3055, ['武昌', '洪山', '江汉', '汉阳', '硚口', '青山']),
    ('南京', 32.0603, 118.7969, ['鼓楼', '玄武', '建邺', '秦淮', '栖霞', '雨花台']),
    ('西安', 34.3416, 108.9398, ['雁塔', '碑林', '莲湖', '新城', '未央', '灞桥']),
    ('重庆', 29.5630, 106.5516, ['渝中', '江北', '南岸', '九龙坡', '沙坪坝', '渝北']),
]

TYPES = ['整租·一居室', '整租·二居室', '整租·三居室', '合租·主卧', '合租·次卧', 'Loft公寓', '精品公寓', '复式小洋房']
TAGS = ['近地铁', '精装修', '独立阳台', '家电齐全', '可短租', '随时看房', '采光极佳', '包物业', '电梯房', '拎包入住']
STREETS = ['中山路', '人民路', '建设路', '解放路', '青年路', '学院路', '和平路', '科技园路', '滨江路', '文化路', '阳光路', '幸福街']
PRICES = [88, 99, 128, 158, 188, 218, 258, 288, 328, 358, 388, 428, 468, 518, 588, 668, 728, 888]

rows = []
now = datetime.datetime.now()
for i in range(1, 101):
    city, lat0, lng0, dists = random.choice(CITIES)
    dist = random.choice(dists)
    rtype = random.choice(TYPES)
    tags = random.sample(TAGS, k=random.randint(1, 3))
    price = random.choice(PRICES)
    deposit = round(price * random.choice([1, 2, 3]), 0)
    title = f'【{rtype}】{city}·{dist}区 {random.choice(TAGS)} · {random.randint(15, 120)}㎡'
    tag_str = '、'.join(tags[:2])
    desc = (f'{city}市{dist}区核心商圈优质{("房源" if rtype.startswith("整租") else "单间")}，{tag_str}，'
            f'拎包入住，周边配套成熟，交通出行便利。房屋采光充足、隔音良好，'
            f'适合白领、学生及家庭入住，支持在线预约看房与平台担保交易。')
    address = f'{city}市{dist}区{random.choice(STREETS)}{random.randint(1, 999)}号'
    lat = round(lat0 + random.uniform(-0.12, 0.12), 6)
    lng = round(lng0 + random.uniform(-0.12, 0.12), 6)
    rating = round(random.uniform(4.0, 5.0), 1)
    ct = now - datetime.timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
    rows.append((
        title, desc, price, address, lat, lng, rating,
        ','.join(tags), 1, 0, ct, ct, 2, deposit, '', ''
    ))

sql = (
    "INSERT INTO room (title, description, price, address, latitude, longitude, rating, "
    "tags, status, version, create_time, update_time, landlord_id, deposit, cover, detail_images) "
    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
)
cur.executemany(sql, rows)
conn.commit()
print('inserted:', len(rows))
cur.close()
conn.close()
