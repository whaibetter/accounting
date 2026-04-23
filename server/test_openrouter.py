from app.auth import create_access_token
import httpx
import json

# 获取访问Token
token = create_access_token()
headers = {'Authorization': 'Bearer ' + token}

# 1. 配置OpenRouter API
config_data = {
    "provider": "openai",
    "api_key": "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",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "minimax/minimax-m2.5:free",
    "temperature": 0.3,
    "max_tokens": 1024,
    "timeout": 60  # 增加超时时间
}

print("1. 配置OpenRouter API...")
client = httpx.Client(timeout=30)
r = client.put('http://localhost:8000/api/v1/llm/config', headers=headers, json=config_data)
print(f"配置状态: {r.status_code}")
print(f"配置结果: {r.text[:500]}")

# 2. 测试连接 - 使用更长的超时
print("\n2. 测试API连接...")
try:
    r2 = client.post('http://localhost:8000/api/v1/llm/test', headers=headers, timeout=60)
    print(f"测试状态: {r2.status_code}")
    print(f"测试结果: {r2.text}")
except Exception as e:
    print(f"测试失败: {str(e)}")

# 3. 测试文本解析
print("\n3. 测试文本解析...")
test_text = "今天买咖啡花了35元"
try:
    r3 = client.post('http://localhost:8000/api/v1/llm/parse', headers=headers, json={'text': test_text}, timeout=60)
    print(f"解析状态: {r3.status_code}")
    print(f"解析结果: {r3.text}")
except Exception as e:
    print(f"解析失败: {str(e)}")

# 4. 测试解析并导入
print("\n4. 测试解析并导入...")
try:
    r4 = client.post('http://localhost:8000/api/v1/llm/parse-import', headers=headers, json={'text': test_text, 'default_account': '现金'}, timeout=60)
    print(f"导入状态: {r4.status_code}")
    print(f"导入结果: {r4.text}")
except Exception as e:
    print(f"导入失败: {str(e)}")

client.close()
