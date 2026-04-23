"""
大模型API集成功能单元测试。

测试范围：
    - LlmConfigManager: 配置存储、加密解密、验证
    - LlmService: 文本解析、JSON提取、数据验证
    - LLM路由: API接口的请求响应

运行方法：
    cd server
    python -m pytest tests/test_llm.py -v
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import date
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from app.llm_config import LlmConfigManager, _encrypt_value, _decrypt_value, DEFAULT_CONFIG
from app.llm_service import LlmService


class TestLlmConfigEncryption:
    """加密解密功能测试。"""

    def test_encrypt_decrypt_roundtrip(self):
        plain = "sk-test-api-key-12345"
        encrypted = _encrypt_value(plain)
        assert encrypted != plain
        decrypted = _decrypt_value(encrypted)
        assert decrypted == plain

    def test_encrypt_empty_string(self):
        assert _encrypt_value("") == ""
        assert _decrypt_value("") == ""

    def test_decrypt_invalid_value(self):
        result = _decrypt_value("invalid-encrypted-value")
        assert result == ""

    def test_encrypt_different_values_produce_different_ciphertext(self):
        enc1 = _encrypt_value("key1")
        enc2 = _encrypt_value("key2")
        assert enc1 != enc2


class TestLlmConfigManager:
    """配置管理器测试。"""

    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.tmp_dir) / "test_llm_config.json"
        self.manager = LlmConfigManager(config_file=self.config_file)

    def teardown_method(self):
        if self.config_file.exists():
            os.unlink(self.config_file)
        os.rmdir(self.tmp_dir)

    def test_get_default_config_when_no_file(self):
        config = self.manager.get_config()
        assert config["provider"] == "openai"
        assert config["temperature"] == 0.3
        assert config["max_tokens"] == 1024
        assert config["api_key"] == ""

    def test_update_and_read_config(self):
        result = self.manager.update_config(
            provider="anthropic",
            api_key="sk-ant-test-key",
            temperature=0.5,
        )
        assert result["provider"] == "anthropic"
        assert result["api_key"] == "sk-ant-test-key"
        assert result["temperature"] == 0.5

        config = self.manager.get_config()
        assert config["provider"] == "anthropic"
        assert config["api_key"] == "sk-ant-test-key"

    def test_api_key_encrypted_on_disk(self):
        self.manager.update_config(api_key="sk-super-secret-key")

        with open(self.config_file, "r") as f:
            raw = json.load(f)

        assert raw["api_key"] != "sk-super-secret-key"
        assert raw["api_key"] != ""

    def test_is_configured_false_by_default(self):
        assert self.manager.is_configured() is False

    def test_is_configured_true_after_setting_key(self):
        self.manager.update_config(api_key="sk-test", provider="openai")
        assert self.manager.is_configured() is True

    def test_update_config_validates_provider(self):
        with pytest.raises(ValueError, match="不支持的提供商"):
            self.manager.update_config(provider="invalid_provider")

    def test_update_config_validates_temperature(self):
        with pytest.raises(ValueError, match="temperature"):
            self.manager.update_config(temperature=3.0)

    def test_update_config_validates_max_tokens(self):
        with pytest.raises(ValueError, match="max_tokens"):
            self.manager.update_config(max_tokens=50000)

    def test_update_config_validates_timeout(self):
        with pytest.raises(ValueError, match="timeout"):
            self.manager.update_config(timeout=200)

    def test_get_resolved_config_fills_defaults(self):
        self.manager.update_config(provider="openai", api_key="sk-test")
        config = self.manager.get_resolved_config()
        assert config["base_url"] == "https://api.openai.com/v1"
        assert config["model"] == "gpt-4o-mini"

    def test_get_resolved_config_anthropic_defaults(self):
        self.manager.update_config(provider="anthropic", api_key="sk-ant-test")
        config = self.manager.get_resolved_config()
        assert config["base_url"] == "https://api.anthropic.com"
        assert config["model"] == "claude-sonnet-4-20250514"

    def test_get_providers(self):
        providers = self.manager.get_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "custom" in providers
        assert providers["openai"]["name"] == "OpenAI"

    def test_partial_update_preserves_other_fields(self):
        self.manager.update_config(provider="openai", api_key="sk-test", temperature=0.7)
        self.manager.update_config(temperature=0.5)

        config = self.manager.get_config()
        assert config["provider"] == "openai"
        assert config["api_key"] == "sk-test"
        assert config["temperature"] == 0.5


class TestLlmServiceExtractBills:
    """文本解析和JSON提取测试。"""

    def setup_method(self):
        self.service = LlmService()

    def test_extract_bills_from_plain_json(self):
        raw = '[{"type":1,"amount":35.0,"category":"饮料","date":"2026-04-22","time":null,"remark":"买咖啡","account":null,"payment_method":null}]'
        bills = self.service._extract_bills(raw)
        assert len(bills) == 1
        assert bills[0]["amount"] == 35.0
        assert bills[0]["category"] == "饮料"

    def test_extract_bills_from_json_code_block(self):
        raw = '```json\n[{"type":1,"amount":28.0,"category":"午餐","date":"2026-04-22","time":null,"remark":"午饭","account":null,"payment_method":null}]\n```'
        bills = self.service._extract_bills(raw)
        assert len(bills) == 1
        assert bills[0]["amount"] == 28.0

    def test_extract_bills_from_code_block_without_language(self):
        raw = '```\n[{"type":1,"amount":15.0,"category":"打车","date":"2026-04-22","time":null,"remark":"打车回家","account":null,"payment_method":null}]\n```'
        bills = self.service._extract_bills(raw)
        assert len(bills) == 1

    def test_extract_bills_multiple(self):
        raw = '[{"type":1,"amount":28.0,"category":"午餐","date":"2026-04-22","time":null,"remark":"午饭","account":null,"payment_method":null},{"type":1,"amount":15.0,"category":"打车","date":"2026-04-22","time":null,"remark":"打车回家","account":null,"payment_method":null}]'
        bills = self.service._extract_bills(raw)
        assert len(bills) == 2

    def test_extract_bills_from_dict_with_bills_key(self):
        raw = '{"bills":[{"type":1,"amount":35.0,"category":"饮料","date":"2026-04-22","time":null,"remark":"买咖啡","account":null,"payment_method":null}]}'
        bills = self.service._extract_bills(raw)
        assert len(bills) == 1

    def test_extract_bills_empty_response(self):
        assert self.service._extract_bills("") == []
        assert self.service._extract_bills(None) == []

    def test_extract_bills_invalid_json(self):
        raw = "This is not JSON at all"
        assert self.service._extract_bills(raw) == []


class TestLlmServiceValidateBill:
    """账单数据验证和修正测试。"""

    def setup_method(self):
        self.service = LlmService()

    def test_validate_complete_bill(self):
        bill = {
            "type": 1,
            "amount": 35.0,
            "category": "饮料",
            "date": "2026-04-22",
            "time": "14:30",
            "remark": "买咖啡",
            "account": None,
            "payment_method": None,
        }
        self.service._validate_and_fix_bill(bill)
        assert bill["type"] == 1
        assert bill["amount"] == 35.0

    def test_validate_fix_missing_type(self):
        bill = {"amount": 50, "category": "午餐", "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["type"] == 1

    def test_validate_fix_invalid_type(self):
        bill = {"type": 5, "amount": 50, "category": "午餐", "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["type"] == 1

    def test_validate_fix_negative_amount(self):
        bill = {"type": 1, "amount": -35.0, "category": "饮料", "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["amount"] == 35.0

    def test_validate_fix_missing_date(self):
        bill = {"type": 1, "amount": 35, "category": "饮料"}
        self.service._validate_and_fix_bill(bill)
        assert bill["date"] == date.today().isoformat()

    def test_validate_fix_missing_category(self):
        bill = {"type": 1, "amount": 35, "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["category"] == "其他"

    def test_validate_fix_missing_remark(self):
        bill = {"type": 1, "amount": 35, "category": "饮料", "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["remark"] == ""

    def test_validate_fix_string_amount(self):
        bill = {"type": 1, "amount": "35.5", "category": "饮料", "date": "2026-04-22"}
        self.service._validate_and_fix_bill(bill)
        assert bill["amount"] == 35.5

    def test_validate_non_dict_input(self):
        bill = "not a dict"
        self.service._validate_and_fix_bill(bill)


class TestLlmServiceNormalizeDate:
    """日期标准化测试。"""

    def setup_method(self):
        self.service = LlmService()

    def test_normalize_iso_date(self):
        assert self.service._normalize_date("2026-04-22") == "2026-04-22"

    def test_normalize_slash_date(self):
        assert self.service._normalize_date("2026/04/22") == "2026-04-22"

    def test_normalize_chinese_date(self):
        assert self.service._normalize_date("2026年04月22日") == "2026-04-22"

    def test_normalize_invalid_date_returns_today(self):
        result = self.service._normalize_date("invalid")
        assert result == date.today().isoformat()


class TestLlmServiceNormalizeTime:
    """时间标准化测试。"""

    def setup_method(self):
        self.service = LlmService()

    def test_normalize_standard_time(self):
        assert self.service._normalize_time("14:30") == "14:30"

    def test_normalize_single_digit_hour(self):
        assert self.service._normalize_time("9:30") == "09:30"

    def test_normalize_invalid_time(self):
        assert self.service._normalize_time("invalid") is None


class TestLlmServiceParseText:
    """文本解析集成测试（不调用真实API）。"""

    def setup_method(self):
        self.service = LlmService()

    @pytest.mark.asyncio
    async def test_parse_empty_text(self):
        result = await self.service.parse_text("")
        assert result["success"] is False
        assert "不能为空" in result["error"]

    @pytest.mark.asyncio
    async def test_parse_too_long_text(self):
        result = await self.service.parse_text("x" * 2001)
        assert result["success"] is False
        assert "过长" in result["error"]

    @pytest.mark.asyncio
    async def test_parse_without_config(self):
        tmp_dir = tempfile.mkdtemp()
        config_file = Path(tmp_dir) / "test_config.json"
        self.service.config_manager = LlmConfigManager(config_file=config_file)

        result = await self.service.parse_text("今天买咖啡花了35元")
        assert result["success"] is False
        assert "未配置" in result["error"]

        if config_file.exists():
            os.unlink(config_file)
        os.rmdir(tmp_dir)

    @pytest.mark.asyncio
    async def test_parse_with_mock_api(self):
        tmp_dir = tempfile.mkdtemp()
        config_file = Path(tmp_dir) / "test_config.json"
        manager = LlmConfigManager(config_file=config_file)
        manager.update_config(provider="openai", api_key="sk-test-key")
        self.service.config_manager = manager

        mock_response = '[{"type":1,"amount":35.0,"category":"饮料","date":"2026-04-22","time":null,"remark":"买咖啡","account":null,"payment_method":null}]'

        with patch.object(self.service, '_call_openai', new_callable=AsyncMock, return_value=mock_response):
            result = await self.service.parse_text("今天买咖啡花了35元")
            assert result["success"] is True
            assert len(result["bills"]) == 1
            assert result["bills"][0]["amount"] == 35.0
            assert result["bills"][0]["category"] == "饮料"

        if config_file.exists():
            os.unlink(config_file)
        os.rmdir(tmp_dir)


class TestLlmServiceTestConnection:
    """连接测试。"""

    @pytest.mark.asyncio
    async def test_test_connection_without_config(self):
        tmp_dir = tempfile.mkdtemp()
        config_file = Path(tmp_dir) / "test_config.json"
        service = LlmService()
        service.config_manager = LlmConfigManager(config_file=config_file)

        result = await service.test_connection()
        assert result["success"] is False
        assert "未配置" in result["message"]

        if config_file.exists():
            os.unlink(config_file)
        os.rmdir(tmp_dir)
