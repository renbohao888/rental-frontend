#!/usr/bin/env python3
"""
随机房源数据插入脚本
在指定房东账号(account_no='88888888')下插入 100 条随机房源记录
用法: python insert_random_rooms.py
"""
import pymysql, random
from datetime import datetime, timedelta

# ========== 配置 ==========
DB_CONFIG = {
    "host": "localhost", "port": 3306,
    "user": "root", "password": "1232731qW",
    "database": "room_rent_db", "charset": "utf8mb4",
}
LANDLORD_ACCOUNT = "88888888"
COUNT = 100

# ========== 随机数据池 ==========
COMMUNITIES = ["阳光花园","翠苑新村","金色家园","绿城百合","万科城","碧桂园","龙湖春江","中海国际","保利天汇","华润橡树湾","招商雍华府","金地自在城","融创壹号院","恒大华府","世茂滨江","新城璞樾","旭辉公元","中南林樾","正荣府","中梁首府","远洋天骄","首创光和城","泰禾金府","蓝光雍锦","佳兆业广场"]
ROOM_TYPES = ["精装一室户","阳光大主卧","温馨次卧","整租一居室","两室一厅整租","三室两厅豪华套","loft复式公寓","花园洋房","电梯高层景观房","独立厨卫单间","朝南主卧带阳台","北欧风两居","地铁口精装公寓","独栋别墅整租","合租单间带独卫"]
SUFFIXES = ["拎包入住","品牌家电","全新装修","采光无敌","安静舒适","交通便利","生活配套齐全","管家服务","密码锁安全","定期保洁",""]
ADDRESSES = ["北京市朝阳区建国路88号","北京市海淀区中关村南大街5号","北京市西城区金融街16号","北京市东城区东直门外大街22号","北京市丰台区马家堡东路18号","北京市通州区新华西街55号","上海市浦东新区世纪大道100号","上海市静安区南京西路1266号","上海市徐汇区衡山路12号","上海市长宁区延安西路2000号","上海市闵行区七莘路333号","上海市杨浦区五角场800号","广州市天河区珠江新城华夏路10号","广州市越秀区北京路188号","广州市海珠区新港中路350号","深圳市南山区科技园南路28号","深圳市福田区深南大道6008号","深圳市罗湖区东门中路2000号","杭州市西湖区文三路508号","杭州市滨江区江南大道88号","杭州市上城区延安路288号","成都市锦江区春熙路99号","成都市武侯区科华北路58号","成都市高新区天府大道北段1600号","武汉市武昌区中南路99号","南京市鼓楼区中山北路200号","重庆渝中区解放碑88号"]
TAG_POOLS = [["近地铁","拎包入住","精装修"],["近地铁","独立卫生间","朝南"],["拎包入住","品牌家电","电梯房"],["近地铁","密码锁","定期保洁"],["独立厨卫","朝南","采光好"],["精装修","管家服务","安静"],["近地铁","电梯房","生活便利"],["拎包入住","朝南","带阳台"],["品牌家电","密码锁","地铁口"],["精装修","独立厨卫","电梯房"],["近地铁","带阳台","安静舒适"],["拎包入住","管家服务","采光无敌"]]
DESCS = ["房间宽敞明亮，装修精美，家具家电齐全，拎包即可入住。小区环境优美，物业管理完善。","全新精装修，品牌家电一应俱全。南北通透，采光极佳。小区绿化率高，生活便利。","房东直租，无中介费。房间干净整洁，独立卫浴，私密性好。临近地铁站通勤方便。","高品质公寓，智能门锁安全放心。周边商场超市林立餐饮娱乐一应俱全。","温馨舒适居住空间，朝南大窗采光充足。厨房设施齐全可做饭。社区安静适合白领。","现代化装修风格简约大方。布局合理储物空间充足。小区配有健身房游泳池等设施。","地铁口步行5分钟，公交线路众多。房间保养如新，定期保洁服务让您住得舒心。","花园小区环境清幽。房间带独立阳台可观景可晾晒。邻居素质高居住氛围好。"]
COVER_URLS = [f"https://picsum.photos/seed/room{i}/800/600" for i in range(1, 31)]

# ========== 生成随机房源 ==========
def generate_rooms(landlord_id, n):
    rooms = []
    now = datetime.now()
    for i in range(1, n + 1):
        title = f"{random.choice(COMMUNITIES)} {random.choice(ROOM_TYPES)}"
        sfx = random.choice(SUFFIXES)
        if sfx:
            title += f" {sfx}"
        price = round(random.uniform(500, 8000), 2)
        deposit = round(price * random.choice([1, 2, 3]), 2)
        status = random.choices([0, 1, 3], weights=[10, 80, 10])[0]
        days_ago = random.randint(0, 90)
        ct = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        ct_str = ct.strftime("%Y-%m-%d %H:%M:%S")
        cover_cnt = random.randint(1, 3)
        covers = ",".join(random.sample(COVER_URLS, cover_cnt))
        detail_cnt = random.randint(3, 6)
        detail_start = random.randint(1, 20)
        details = ",".join([f"https://picsum.photos/seed/detail{detail_start + j}/1200/800" for j in range(detail_cnt)])
        rooms.append({
            "title": title,
            "description": random.choice(DESCS),
            "price": price,
            "address": random.choice(ADDRESSES),
            "landlord_id": landlord_id,
            "cover": covers,
            "detail_images": details,
            "latitude": round(random.uniform(22.0, 40.0), 7),
            "longitude": round(random.uniform(100.0, 122.0), 7),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "tags": ",".join(random.choice(TAG_POOLS)),
            "deposit": deposit,
            "status": status,
            "version": 0,
            "create_time": ct_str,
            "update_time": ct_str,
        })
    return rooms


# ========== 主函数 ==========
def main():
    print("=" * 55)
    print("  随机房源数据插入脚本")
    print(f"  房东账号: {LANDLORD_ACCOUNT}  |  目标: {COUNT} 条")
    print("=" * 55)

    # 连接数据库
    print(f"\n[1/4] 连接 {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']} ...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("  OK 数据库已连接")
    except Exception as e:
        print(f"  FAIL 连接失败: {e}")
        return

    try:
        # 查找房东
        print(f"\n[2/4] 查找房东 account_no='{LANDLORD_ACCOUNT}' ...")
        cur.execute("SELECT id, account_no, nickname, role FROM user WHERE account_no = %s", (LANDLORD_ACCOUNT,))
        row = cur.fetchone()
        if not row:
            print(f"  FAIL 未找到账号 '{LANDLORD_ACCOUNT}'")
            return
        lid, acc, nick, role = row
        role_names = {0: "管理员", 1: "房东", 2: "租客"}
        if role != 1:
            print(f"  WARN 该用户角色是「{role_names.get(role, role)}」而非房东，将继续插入...")
        print(f"  OK 房东: ID={lid}  昵称={nick}  角色={role_names.get(role, role)}")

        # 生成数据
        print(f"\n[3/4] 生成 {COUNT} 条随机房源...")
        rooms = generate_rooms(lid, COUNT)
        print(f"  OK 已生成 {len(rooms)} 条")

        # 插入数据
        print(f"\n[4/4] 写入 room 表...")
        sql = """INSERT INTO room (title,description,price,address,landlord_id,cover,detail_images,
                  latitude,longitude,rating,tags,deposit,status,version,create_time,update_time)
                  VALUES (%(title)s,%(description)s,%(price)s,%(address)s,%(landlord_id)s,
                  %(cover)s,%(detail_images)s,%(latitude)s,%(longitude)s,%(rating)s,
                  %(tags)s,%(deposit)s,%(status)s,%(version)s,%(create_time)s,%(update_time)s)"""
        ok = 0
        batch = 20
        for i in range(0, len(rooms), batch):
            chunk = rooms[i:i + batch]
            try:
                cur.executemany(sql, chunk)
                conn.commit()
                ok += len(chunk)
                print(f"  已写入 {ok}/{COUNT} 条...")
            except Exception as e:
                conn.rollback()
                print(f"  FAIL 批次[{i+1}-{min(i+batch, len(rooms))}]失败: {e}")
                for r in chunk:
                    try:
                        cur.execute(sql, r)
                        conn.commit()
                        ok += 1
                    except Exception as e2:
                        print(f"    跳过: {r['title'][:30]}... {e2}")
                print(f"  已写入 {ok}/{COUNT} 条...")

        # 统计
        cur.execute("SELECT status, COUNT(*) FROM room WHERE landlord_id = %s GROUP BY status", (lid,))
        stats = cur.fetchall()
        smap = {0: "待审核", 1: "已上架", 2: "已租出", 3: "已下架", 4: "已驳回"}
        print(f"\n{'='*55}")
        print(f"  完成! 成功: {ok}/{COUNT} 条  |  房东 ID={lid}")
        for s in stats:
            print(f"    {smap.get(s[0], s[0])}: {s[1]} 条")
        print(f"{'='*55}")

    except Exception as e:
        conn.rollback()
        print(f"\n  FAIL: {e}")
        import traceback; traceback.print_exc()
    finally:
        cur.close()
        conn.close()
        print("\n  连接已关闭。Done!")


if __name__ == "__main__":
    main()
