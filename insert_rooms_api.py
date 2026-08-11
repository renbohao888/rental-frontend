#!/usr/bin/env python3
"""
通过 Railway 后端 API 插入 100 条随机房源
用法: python insert_rooms_api.py
"""
import requests, random

BASE = "https://rental-backend-production-78b4.up.railway.app/api"
ACC = "88888888"
PWD = "123456"
COUNT = 100
HEADERS = {"Content-Type": "application/json"}

def api(method, path, payload=None, token=None):
    h = {**HEADERS}
    if token: h["Authorization"] = token
    url = BASE + path
    try:
        r = requests.request(method, url, json=payload, headers=h, timeout=20)
        try:
            return r.status_code, r.json()
        except:
            return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

# 数据池 (精简)
COMMUNITIES = ["阳光花园","翠苑新村","金色家园","绿城百合","万科城","碧桂园","龙湖春江","中海国际","保利天汇","华润橡树湾","招商雍华府","金地自在城","融创壹号院","恒大华府","世茂滨江","新城璞樾","旭辉公元","中南林樾","正荣府","中梁首府","远洋天骄","首创光和城","泰禾金府","蓝光雍锦","佳兆业广场"]
TYPES = ["精装一室户","阳光大主卧","温馨次卧","整租一居室","两室一厅整租","三室两厅豪华套","loft复式公寓","花园洋房","电梯高层景观房","独立厨卫单间","朝南主卧带阳台","北欧风两居","地铁口精装公寓","独栋别墅整租","合租单间带独卫"]
SUFFIXES = ["拎包入住","品牌家电","全新装修","采光无敌","安静舒适","交通便利","生活配套齐全","管家服务","密码锁安全","定期保洁",""]
ADDRESSES = ["北京市朝阳区建国路88号","北京市海淀区中关村南大街5号","北京市西城区金融街16号","北京市东城区东直门外大街22号","北京市丰台区马家堡东路18号","北京市通州区新华西街55号","上海市浦东新区世纪大道100号","上海市静安区南京西路1266号","上海市徐汇区衡山路12号","上海市长宁区延安西路2000号","上海市闵行区七莘路333号","广州市天河区珠江新城华夏路10号","广州市越秀区北京路188号","深圳市南山区科技园南路28号","深圳市福田区深南大道6008号","杭州市西湖区文三路508号","杭州市滨江区江南大道88号","杭州市上城区延安路288号","成都市锦江区春熙路99号","成都市武侯区科华北路58号","武汉市武昌区中南路99号","南京市鼓楼区中山北路200号","重庆渝中区解放碑88号"]
TAG_POOLS = ["近地铁,拎包入住,精装修","近地铁,独立卫生间,朝南","拎包入住,品牌家电,电梯房","近地铁,密码锁,定期保洁","独立厨卫,朝南,采光好","精装修,管家服务,安静","近地铁,电梯房,生活便利","拎包入住,朝南,带阳台","品牌家电,密码锁,地铁口","精装修,独立厨卫,电梯房","近地铁,带阳台,安静舒适","拎包入住,管家服务,采光无敌"]
DESCS = ["房间宽敞明亮，装修精美，家具家电齐全，拎包即可入住。小区环境优美，物业管理完善。","全新精装修，品牌家电一应俱全。南北通透，采光极佳。小区绿化率高，配套成熟，生活便利。","房东直租，无中介费。房间干净整洁，独立卫浴，私密性好。临近地铁站，通勤方便快捷。","高品质公寓，智能门锁安全放心。周边商场超市林立，餐饮娱乐一应俱全，生活丰富多彩。","温馨舒适居住空间，朝南大窗采光充足。厨房设施齐全可做饭。社区安静，适合白领居住。","现代化装修风格简约大方。房间布局合理，储物空间充足。小区配有健身房游泳池等设施。","地铁口步行5分钟，公交线路众多。房间保养如新，定期保洁服务让您住得舒心。","花园小区环境清幽。房间带有独立阳台可观景可晾晒。邻居素质高居住氛围好。"]

print("="*50)
print(f"  通过 API 插入 {COUNT} 条房源到 Railway")
print(f"  后端: {BASE}")
print(f"  房东: {ACC}")
print("="*50)

# 1. 登录
print("\n[1/3] 登录...")
code, r = api("POST", "/user/login", {"accountNo": ACC, "password": PWD})
if code != 200 or not isinstance(r, dict) or not r.get("data", {}).get("token"):
    print(f"  FAIL: {r}")
    exit(1)
token = r["data"]["token"]
print(f"  OK Token 获取成功")

# 2. 插入
print(f"\n[2/3] 插入 {COUNT} 条...")
ok = 0
for i in range(1, COUNT + 1):
    title = f"{random.choice(COMMUNITIES)} {random.choice(TYPES)}"
    sfx = random.choice(SUFFIXES)
    if sfx: title += f" {sfx}"
    body = {
        "title": title,
        "description": random.choice(DESCS),
        "price": round(random.uniform(500, 8000), 2),
        "address": random.choice(ADDRESSES),
        "latitude": round(random.uniform(22, 40), 7),
        "longitude": round(random.uniform(100, 122), 7),
        "rating": round(random.uniform(3.5, 5.0), 1),
        "tags": random.choice(TAG_POOLS),
        "deposit": round(round(random.uniform(500, 8000), 2) * random.choice([1, 2, 3]), 2),
    }
    code, resp = api("POST", "/room/add", body, token=token)
    if code == 200:
        ok += 1
        if ok % 20 == 0: print(f"  已插入 {ok}/{COUNT} 条...")
    else:
        msg = resp.get("message", str(resp)[:80]) if isinstance(resp, dict) else str(resp)[:80]
        print(f"  [{i}] FAIL: {msg}")

print(f"  OK 成功: {ok}/{COUNT}")

# 3. 验证
print(f"\n[3/3] 验证热门房源...")
code, r = api("GET", "/room/recommend/hot?limit=5")
if code == 200 and isinstance(r, dict) and r.get("code") == 200:
    rooms = r.get("data", [])
    print(f"  OK 热门房源返回 {len(rooms)} 条:")
    for rm in rooms[:3]:
        print(f"    - {rm.get('title','?')}  ¥{rm.get('price','?')}")
else:
    print(f"  WARN: {r}")
print(f"\n{'='*50}")
print(f"  完成! 刷新网站即可看到新数据")
print(f"{'='*50}")
