"""
大模型API调用服务模块。

功能描述：
    封装大模型API的调用逻辑，支持：
    - OpenAI格式API调用（兼容OpenAI、DeepSeek、通义千问等）
    - Anthropic格式API调用（兼容Claude系列）
    - 自定义API端点调用
    - 连接测试
    - 自然语言文本解析为结构化记账数据

使用方法：
    from app.llm_service import LlmService

    service = LlmService()
    result = await service.test_connection()
    parsed = await service.parse_text("今天买咖啡花了35元")

异常处理：
    - API密钥未配置时抛出ValueError
    - 网络连接失败时抛出httpx.HTTPError
    - API返回错误时抛出RuntimeError
"""

import json
import re
import logging
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx

from app.llm_config import LlmConfigManager

logger = logging.getLogger(__name__)


def _mask_api_key(api_key: str) -> str:
    if not api_key:
        return "(空)"
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


def _log_request(url: str, method: str, payload: Dict, headers: Dict, provider: str):
    safe_headers = {k: (_mask_api_key(v) if "key" in k.lower() or "auth" in k.lower() else v) for k, v in headers.items()}
    logger.info("=" * 60)
    logger.info(f"[LLM API 请求开始] 提供商: {provider}")
    logger.info(f"  URL: {url}")
    logger.info(f"  方法: {method}")
    logger.info(f"  请求头: {json.dumps(safe_headers, ensure_ascii=False)}")
    logger.info(f"  请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")


def _log_response(status_code: int, response_text: str, elapsed_ms: float, success: bool = True):
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"[LLM API 响应] 状态码: {status_code}, 耗时: {elapsed_ms:.0f}ms")
    try:
        resp_json = json.loads(response_text)
        logger.log(level, f"  响应内容: {json.dumps(resp_json, ensure_ascii=False, indent=2)[:2000]}")
    except json.JSONDecodeError:
        logger.log(level, f"  响应内容(文本): {response_text[:1000]}")
    logger.info("=" * 60)


def _log_error(error: Exception, elapsed_ms: float):
    logger.error(f"[LLM API 错误] 耗时: {elapsed_ms:.0f}ms")
    logger.error(f"  错误类型: {type(error).__name__}")
    logger.error(f"  错误信息: {str(error)}")
    logger.info("=" * 60)

SYSTEM_PROMPT = """你是一个专业的记账助手。你的任务是将用户输入的自然语言记账描述转换为结构化的JSON数据。

## 输出格式要求
你必须输出一个JSON数组，每个元素代表一笔账单，格式如下：
```json
[
  {
    "type": 1,
    "amount": 35.0,
    "category": "咖啡",
    "date": "2026-04-22",
    "time": null,
    "remark": "买咖啡",
    "account": null,
    "payment_method": null
  }
]
```

## 字段说明
- type: 账单类型，1=支出，2=收入
- amount: 金额，正数，单位为元
- category: 分类名称，必须是以下预设分类之一
- date: 日期，格式YYYY-MM-DD
- time: 时间，格式HH:MM，可为null
- remark: 备注描述
- account: 账户名称，可为null（使用默认账户）
- payment_method: 支付方式，可为null

## 预设支出分类
餐饮（早餐、午餐、晚餐、零食、饮料）、交通（公交、地铁、打车、加油、停车）、购物（日用品、衣物、数码、美妆）、居住（房租、水电、物业、网费）、娱乐（电影、游戏、旅行、运动）、医疗（门诊、药品、体检）、教育（书籍、课程、培训）、通讯（话费、会员）、人情（红包、礼物、请客）、其他

## 预设收入分类
工资、兼职、理财、红包、退款、其他

## 解析规则
1. 金额提取：识别"XX元"、"XX块"、"XX块钱"、"¥XX"、"$XX"等金额表达
2. 日期提取：
   - "今天" → 当前日期
   - "昨天" → 当前日期-1
   - "前天" → 当前日期-2
   - "X号/X日" → 当月X日
   - "X月X日" → 对应日期
   - 无日期信息 → 当前日期
3. 时间提取：识别"早上X点"、"下午X点"、"晚上X点"、"X点"等时间表达
4. 分类推断：根据消费内容自动推断最匹配的分类
5. 类型判断：默认为支出，出现"收入"、"收到"、"工资"等关键词时为收入
6. 多笔账单：如果用户描述了多笔消费，分别输出

## 示例
输入："今天买咖啡花了35元"
输出：
```json
[{"type":1,"amount":35.0,"category":"饮料","date":"2026-04-22","time":null,"remark":"买咖啡","account":null,"payment_method":null}]
```

输入："昨天午饭28块，打车回家15"
输出：
```json
[{"type":1,"amount":28.0,"category":"午餐","date":"2026-04-21","time":null,"remark":"午饭","account":null,"payment_method":null},{"type":1,"amount":15.0,"category":"打车","date":"2026-04-21","time":null,"remark":"打车回家","account":null,"payment_method":null}]
```

输入："3月工资到账15000"
输出：
```json
[{"type":2,"amount":15000.0,"category":"工资","date":"2026-03-01","time":null,"remark":"3月工资","account":null,"payment_method":null}]
```

重要：只输出JSON数据，不要输出任何其他文字说明。"""


class LlmService:
    """
    大模型API调用服务。

    支持OpenAI和Anthropic两种API格式，
    提供连接测试和文本解析功能。

    Attributes:
        config_manager: 配置管理器实例
    """

    def __init__(self):
        self.config_manager = LlmConfigManager()

    def _get_client(self) -> httpx.AsyncClient:
        """
        创建HTTP客户端。

        根据配置的timeout创建异步HTTP客户端。

        Returns:
            httpx.AsyncClient: 异步HTTP客户端
        """
        config = self.config_manager.get_resolved_config()
        timeout = config.get("timeout", 30)
        return httpx.AsyncClient(timeout=float(timeout))

    async def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接是否正常。

        发送一个简单的请求验证API密钥和端点是否可用。

        Returns:
            Dict[str, Any]: 测试结果，包含success、message、model等字段

        Raises:
            ValueError: API未配置时
        """
        if not self.config_manager.is_configured():
            return {
                "success": False,
                "message": "API未配置，请先设置API密钥和提供商",
            }

        config = self.config_manager.get_resolved_config()
        provider = config.get("provider", "openai")

        try:
            if provider == "anthropic":
                return await self._test_anthropic(config)
            else:
                return await self._test_openai(config)
        except httpx.ConnectError:
            return {
                "success": False,
                "message": f"无法连接到API服务器 {config.get('base_url', '')}",
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "连接超时，请检查网络或增加超时时间",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}",
            }

    async def _test_openai(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试OpenAI格式API连接。

        Args:
            config: 解析后的配置

        Returns:
            Dict[str, Any]: 测试结果
        """
        base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"

        payload = {
            "model": config.get("model", "gpt-4o-mini"),
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
        }
        headers = {
            "Authorization": f"Bearer {config.get('api_key', '')}",
            "Content-Type": "application/json",
        }

        async with self._get_client() as client:
            resp = await client.post(url, json=payload, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                model = data.get("model", config.get("model", ""))
                return {
                    "success": True,
                    "message": f"连接成功，模型: {model}",
                    "model": model,
                }
            elif resp.status_code == 401:
                return {"success": False, "message": "API密钥无效"}
            elif resp.status_code == 429:
                return {"success": False, "message": "API调用频率超限，请稍后重试"}
            else:
                return {
                    "success": False,
                    "message": f"API返回错误 (HTTP {resp.status_code}): {resp.text[:200]}",
                }

    async def _test_anthropic(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试Anthropic格式API连接。

        Args:
            config: 解析后的配置

        Returns:
            Dict[str, Any]: 测试结果
        """
        base_url = config.get("base_url", "https://api.anthropic.com").rstrip("/")
        url = f"{base_url}/v1/messages"

        payload = {
            "model": config.get("model", "claude-sonnet-4-20250514"),
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
        }
        headers = {
            "x-api-key": config.get("api_key", ""),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with self._get_client() as client:
            resp = await client.post(url, json=payload, headers=headers)

            if resp.status_code == 200:
                model = config.get("model", "")
                return {
                    "success": True,
                    "message": f"连接成功，模型: {model}",
                    "model": model,
                }
            elif resp.status_code == 401:
                return {"success": False, "message": "API密钥无效"}
            elif resp.status_code == 429:
                return {"success": False, "message": "API调用频率超限，请稍后重试"}
            else:
                return {
                    "success": False,
                    "message": f"API返回错误 (HTTP {resp.status_code}): {resp.text[:200]}",
                }

    async def parse_text(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"success": False, "bills": [], "error": "输入内容不能为空"}

        if len(text) > 2000:
            return {"success": False, "bills": [], "error": "输入内容过长，最多2000字符"}

        if not self.config_manager.is_configured():
            return {"success": False, "bills": [], "error": "API未配置，请先设置API密钥"}

        config = self.config_manager.get_resolved_config()
        provider = config.get("provider", "openai")

        logger.info(f"[智能记账] 开始解析文本: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        logger.info(f"[智能记账] 提供商: {provider}, 模型: {config.get('model', 'unknown')}")

        today = date.today().isoformat()
        user_message = f"当前日期: {today}\n用户输入: {text.strip()}"

        try:
            if provider == "anthropic":
                raw_response = await self._call_anthropic(config, user_message)
            else:
                raw_response = await self._call_openai(config, user_message)

            logger.info(f"[智能记账] 原始响应: {raw_response[:500]}{'...' if len(raw_response) > 500 else ''}")

            bills = self._extract_bills(raw_response)

            if not bills:
                logger.warning(f"[智能记账] 未能解析出有效账单，原始响应: {raw_response[:300]}")
                return {
                    "success": False,
                    "bills": [],
                    "raw_response": raw_response,
                    "error": "未能从AI响应中解析出有效的记账数据",
                }

            for bill in bills:
                self._validate_and_fix_bill(bill)

            logger.info(f"[智能记账] 成功解析 {len(bills)} 条账单: {json.dumps(bills, ensure_ascii=False)}")

            return {
                "success": True,
                "bills": bills,
                "raw_response": raw_response,
            }

        except httpx.ConnectError as e:
            logger.error(f"[智能记账] 连接错误: {e}")
            return {"success": False, "bills": [], "error": "无法连接到API服务器"}
        except httpx.TimeoutException as e:
            logger.error(f"[智能记账] 请求超时: {e}")
            return {"success": False, "bills": [], "error": "API请求超时"}
        except Exception as e:
            logger.error(f"[智能记账] 解析失败: {e}", exc_info=True)
            return {"success": False, "bills": [], "error": f"解析失败: {str(e)}"}

    async def _call_openai(self, config: Dict[str, Any], user_message: str) -> str:
        base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        provider = config.get("provider", "openai")

        payload = {
            "model": config.get("model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT[:200] + "..."},
                {"role": "user", "content": user_message},
            ],
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 1024),
        }
        headers = {
            "Authorization": f"Bearer {config.get('api_key', '')}",
            "Content-Type": "application/json",
        }

        full_payload = {
            "model": config.get("model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 1024),
        }

        _log_request(url, "POST", full_payload, headers, provider)
        start_time = time.time()

        try:
            async with self._get_client() as client:
                resp = await client.post(url, json=full_payload, headers=headers)
                elapsed_ms = (time.time() - start_time) * 1000

                if resp.status_code != 200:
                    _log_response(resp.status_code, resp.text, elapsed_ms, success=False)
                    error_text = resp.text[:500]
                    raise RuntimeError(f"API调用失败 (HTTP {resp.status_code}): {error_text}")

                _log_response(resp.status_code, resp.text, elapsed_ms, success=True)
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"[LLM 解析结果] 内容长度: {len(content)} 字符")
                return content

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            _log_error(e, elapsed_ms)
            raise

    async def _call_anthropic(self, config: Dict[str, Any], user_message: str) -> str:
        base_url = config.get("base_url", "https://api.anthropic.com").rstrip("/")
        url = f"{base_url}/v1/messages"
        provider = config.get("provider", "anthropic")

        payload = {
            "model": config.get("model", "claude-sonnet-4-20250514"),
            "system": SYSTEM_PROMPT[:200] + "...",
            "messages": [{"role": "user", "content": user_message}],
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 1024),
        }
        headers = {
            "x-api-key": config.get("api_key", ""),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        full_payload = {
            "model": config.get("model", "claude-sonnet-4-20250514"),
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_message}],
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 1024),
        }

        _log_request(url, "POST", full_payload, headers, provider)
        start_time = time.time()

        try:
            async with self._get_client() as client:
                resp = await client.post(url, json=full_payload, headers=headers)
                elapsed_ms = (time.time() - start_time) * 1000

                if resp.status_code != 200:
                    _log_response(resp.status_code, resp.text, elapsed_ms, success=False)
                    error_text = resp.text[:500]
                    raise RuntimeError(f"API调用失败 (HTTP {resp.status_code}): {error_text}")

                _log_response(resp.status_code, resp.text, elapsed_ms, success=True)
                data = resp.json()
                content_blocks = data.get("content", [])
                content = "".join(
                    block.get("text", "") for block in content_blocks if block.get("type") == "text"
                )
                logger.info(f"[LLM 解析结果] 内容长度: {len(content)} 字符")
                return content

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            _log_error(e, elapsed_ms)
            raise

    def _extract_bills(self, raw_response: str) -> List[Dict[str, Any]]:
        """
        从API响应中提取账单JSON数据。

        尝试多种方式从响应文本中提取JSON：
        1. 直接解析整个响应
        2. 提取```json```代码块
        3. 提取```代码块
        4. 查找JSON数组

        Args:
            raw_response: API原始响应文本

        Returns:
            List[Dict[str, Any]]: 解析出的账单列表
        """
        if not raw_response:
            return []

        json_str = raw_response.strip()

        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "bills" in parsed:
                return parsed["bills"]
        except json.JSONDecodeError:
            pass

        patterns = [
            r"```json\s*\n?(.*?)\n?\s*```",
            r"```\s*\n?(.*?)\n?\s*```",
            r"(\[[\s\S]*?\])",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, json_str, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match.strip())
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    continue

        return []

    def _validate_and_fix_bill(self, bill: Dict[str, Any]) -> None:
        """
        验证并修正单条账单数据。

        确保账单数据包含必要字段，修正不合理的值。

        Args:
            bill: 账单数据字典，会被原地修改
        """
        if not isinstance(bill, dict):
            return

        if "type" not in bill or bill["type"] not in (1, 2):
            bill["type"] = 1

        amount = bill.get("amount", 0)
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0
        bill["amount"] = abs(amount) if amount != 0 else 0

        if not bill.get("date"):
            bill["date"] = date.today().isoformat()
        else:
            bill["date"] = self._normalize_date(str(bill["date"]))

        if bill.get("time"):
            bill["time"] = self._normalize_time(str(bill["time"]))

        if not bill.get("category"):
            bill["category"] = "其他"

        if not bill.get("remark"):
            bill["remark"] = ""

        if "account" not in bill:
            bill["account"] = None

        if "payment_method" not in bill:
            bill["payment_method"] = None

    def _normalize_date(self, date_str: str) -> str:
        """
        标准化日期格式为YYYY-MM-DD。

        Args:
            date_str: 日期字符串

        Returns:
            str: 标准化后的日期字符串
        """
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date().isoformat()
            except ValueError:
                continue
        return date.today().isoformat()

    def _normalize_time(self, time_str: str) -> Optional[str]:
        """
        标准化时间格式为HH:MM。

        Args:
            time_str: 时间字符串

        Returns:
            Optional[str]: 标准化后的时间字符串，解析失败返回None
        """
        import re as re_module
        match = re_module.match(r"(\d{1,2}):(\d{2})", time_str)
        if match:
            return f"{int(match.group(1)):02d}:{match.group(2)}"
        return None
