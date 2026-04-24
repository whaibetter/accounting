import json
import requests

BASE_URL = "http://localhost:8000/api/v1"

def login():
    resp = requests.post(f"{BASE_URL}/auth/login", json={"password": "a6e823c5"})
    if resp.status_code != 200:
        print(f"登录失败: {resp.text}")
        return None
    return resp.json()["data"]["access_token"]

def import_data(token):
    headers = {"Authorization": f"Bearer {token}"}

    accounts_data = {
        "accounts": [
            {"name": "现金", "type": 1, "icon": "cash", "color": "#4CAF50", "initial_balance": 2000},
            {"name": "招商银行储蓄卡", "type": 2, "icon": "bank_card", "color": "#2196F3", "initial_balance": 50000},
            {"name": "信用卡", "type": 3, "icon": "credit_card", "color": "#F44336", "initial_balance": -3000},
            {"name": "支付宝", "type": 4, "icon": "alipay", "color": "#00BCD4", "initial_balance": 8000},
            {"name": "微信", "type": 5, "icon": "wechat", "color": "#4CAF50", "initial_balance": 3500},
        ]
    }

    resp = requests.post(f"{BASE_URL}/import/accounts", json=accounts_data, headers=headers)
    print(f"导入账户: {resp.json()}")

    bills_data = {
        "bills": []
    }

    expense_items = [
        ("招商银行储蓄卡", "早餐", 1, 15, "豆浆油条"),
        ("招商银行储蓄卡", "早餐", 1, 18, "煎饼果子"),
        ("招商银行储蓄卡", "午餐", 1, 35, "工作餐"),
        ("招商银行储蓄卡", "午餐", 1, 42, "外卖"),
        ("招商银行储蓄卡", "晚餐", 1, 68, "火锅"),
        ("招商银行储蓄卡", "晚餐", 1, 55, "烤鱼"),
        ("招商银行储蓄卡", "零食", 1, 25, "奶茶"),
        ("招商银行储蓄卡", "饮料", 1, 18, "咖啡"),
        ("招商银行储蓄卡", "地铁", 1, 6, "上班通勤"),
        ("招商银行储蓄卡", "公交", 1, 2, "公交"),
        ("支付宝", "打车", 1, 28, "加班打车"),
        ("支付宝", "打车", 1, 35, "雨天打车"),
        ("招商银行储蓄卡", "加油", 1, 350, "汽车加油"),
        ("招商银行储蓄卡", "日用品", 1, 89, "超市采购"),
        ("支付宝", "衣物", 1, 299, "春季外套"),
        ("支付宝", "数码", 1, 1999, "蓝牙耳机"),
        ("微信", "房租", 1, 3500, "4月房租"),
        ("招商银行储蓄卡", "水电", 1, 180, "水电费"),
        ("招商银行储蓄卡", "网费", 1, 100, "宽带费"),
        ("支付宝", "电影", 1, 60, "周末电影"),
        ("微信", "游戏", 1, 68, "游戏充值"),
        ("微信", "运动", 1, 120, "健身房月卡"),
        ("招商银行储蓄卡", "门诊", 1, 200, "感冒看诊"),
        ("招商银行储蓄卡", "药品", 1, 65, "买药"),
        ("支付宝", "书籍", 1, 89, "技术书籍"),
        ("支付宝", "课程", 1, 299, "在线课程"),
        ("招商银行储蓄卡", "话费", 1, 58, "手机话费"),
        ("微信", "会员", 1, 25, "视频会员"),
        ("微信", "红包", 1, 200, "朋友生日红包"),
        ("微信", "请客", 1, 320, "聚餐请客"),
        ("支付宝", "美妆", 1, 168, "护肤品"),
        ("招商银行储蓄卡", "停车", 1, 30, "停车场"),
        ("招商银行储蓄卡", "零食", 1, 32, "下午茶"),
        ("支付宝", "日用品", 1, 56, "洗衣液"),
        ("微信", "礼物", 1, 150, "生日礼物"),
    ]

    income_items = [
        ("招商银行储蓄卡", "工资", 2, 15000, "4月工资"),
        ("招商银行储蓄卡", "工资", 2, 15000, "3月工资"),
        ("招商银行储蓄卡", "工资", 2, 15000, "2月工资"),
        ("支付宝", "兼职", 2, 3000, "周末兼职"),
        ("微信", "红包", 2, 88, "过年红包"),
        ("招商银行储蓄卡", "理财", 2, 450, "基金收益"),
        ("支付宝", "退款", 2, 199, "退货退款"),
        ("招商银行储蓄卡", "兼职", 2, 2000, "项目外包"),
    ]

    import random
    base_day = 1
    for i, (account, category, bill_type, amount, remark) in enumerate(expense_items):
        day = (i % 24) + 1
        month = (i // 24) + 1
        if month > 3:
            month = random.randint(1, 3)
        date_str = f"2026-0{month}-{day:02d}"
        hour = random.randint(7, 22)
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        bills_data["bills"].append({
            "account": account,
            "category": category,
            "type": bill_type,
            "amount": amount,
            "date": date_str,
            "time": time_str,
            "remark": remark,
        })

    for i, (account, category, bill_type, amount, remark) in enumerate(income_items):
        day = random.randint(1, 28)
        month = random.randint(1, 3)
        date_str = f"2026-0{month}-{day:02d}"
        time_str = "09:00"
        bills_data["bills"].append({
            "account": account,
            "category": category,
            "type": bill_type,
            "amount": amount,
            "date": date_str,
            "time": time_str,
            "remark": remark,
        })

    resp = requests.post(f"{BASE_URL}/import/bills", json=bills_data, headers=headers)
    print(f"导入账单: {resp.json()}")

    tags_data = [
        {"name": "工作日", "color": "#7cafd4"},
        {"name": "周末", "color": "#7bc97b"},
        {"name": "必要支出", "color": "#d47b7b"},
        {"name": "可选支出", "color": "#a07bd4"},
        {"name": "投资", "color": "#d4a574"},
    ]

    for tag in tags_data:
        resp = requests.post(f"{BASE_URL}/tags", json=tag, headers=headers)
        if resp.status_code == 200:
            print(f"创建标签: {tag['name']} ✓")
        else:
            print(f"创建标签: {tag['name']} - {resp.json().get('detail', '已存在')}")

    print("\n✅ 演示数据导入完成！")

if __name__ == "__main__":
    token = login()
    if token:
        import_data(token)
