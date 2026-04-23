"""
大模型API配置存储与管理模块。

功能描述：
    管理大模型API的配置信息，包括：
    - API密钥安全存储（AES加密）
    - 多平台配置支持（OpenAI、Anthropic格式）
    - 模型参数配置（temperature、max_tokens等）
    - 配置的读取、更新与验证

使用方法：
    from app.llm_config import LlmConfigManager

    manager = LlmConfigManager()
    config = manager.get_config()
    manager.update_config(api_key="sk-xxx", provider="openai")

安全说明：
    API密钥使用AES-256-CBC加密存储，密钥基于机器特征生成。
    配置文件存储在 data/llm_config.json，权限设为仅所有者可读写。
"""

import json
import os
import hashlib
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_FILE = DATA_DIR / "llm_config.json"

PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "anthropic": {
        "name": "Anthropic",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-sonnet-4-20250514",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    },
    "openrouter": {
        "name": "OpenRouter",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_model": "minimax/minimax-m2.5:free",
        "models": [
            "minimax/minimax-m2.5:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-4-maverick:free",
            "qwen/qwen3-32b:free",
        ],
    },
    "custom": {
        "name": "自定义",
        "default_base_url": "",
        "default_model": "",
        "models": [],
    },
}

DEFAULT_API_KEY = "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"

DEFAULT_CONFIG = {
    "provider": "openrouter",
    "api_key": DEFAULT_API_KEY,
    "base_url": "https://openrouter.ai/api/v1",
    "model": "minimax/minimax-m2.5:free",
    "temperature": 0.3,
    "max_tokens": 1024,
    "timeout": 60,
}


def _get_machine_key() -> bytes:
    """
    基于机器特征生成加密密钥。

    使用项目数据目录路径作为密钥种子，确保同一部署实例的密钥一致性。
    生成Fernet兼容的32字节base64编码密钥。

    Returns:
        bytes: Fernet兼容的加密密钥
    """
    seed = str(DATA_DIR.resolve()) + "accounting_llm_config_salt"
    key_hash = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def _encrypt_value(plain_text: str) -> str:
    """
    使用AES加密敏感值。

    Args:
        plain_text: 明文字符串

    Returns:
        str: 加密后的base64编码字符串
    """
    if not plain_text:
        return ""
    fernet = Fernet(_get_machine_key())
    return fernet.encrypt(plain_text.encode()).decode()


def _decrypt_value(encrypted: str) -> str:
    """
    解密AES加密的值。

    Args:
        encrypted: 加密的base64编码字符串

    Returns:
        str: 解密后的明文字符串
    """
    if not encrypted:
        return ""
    try:
        fernet = Fernet(_get_machine_key())
        return fernet.decrypt(encrypted.encode()).decode()
    except Exception as e:
        logger.warning(f"解密失败: {e}")
        return ""


class LlmConfigManager:
    """
    大模型API配置管理器。

    负责配置的持久化存储、加密解密和验证。
    配置文件使用JSON格式，API密钥字段加密存储。

    Attributes:
        config_file: 配置文件路径
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化配置管理器。

        Args:
            config_file: 配置文件路径，默认为 data/llm_config.json
        """
        self.config_file = config_file or CONFIG_FILE
        DATA_DIR.mkdir(exist_ok=True)

    def get_config(self, decrypt: bool = True) -> Dict[str, Any]:
        """
        获取当前配置。

        读取配置文件并返回配置字典。
        如果配置文件不存在，自动初始化默认配置并保存。

        Args:
            decrypt: 是否解密API密钥，默认True

        Returns:
            Dict[str, Any]: 配置字典
        """
        if not self.config_file.exists():
            self._init_default_config()
            return {**DEFAULT_CONFIG, "api_key": DEFAULT_API_KEY if decrypt else _encrypt_value(DEFAULT_API_KEY)}

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"读取配置文件失败: {e}")
            return {**DEFAULT_CONFIG, "api_key": DEFAULT_API_KEY if decrypt else _encrypt_value(DEFAULT_API_KEY)}

        if decrypt and config.get("api_key"):
            config["api_key"] = _decrypt_value(config["api_key"])

        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]

        return config

    def _init_default_config(self) -> None:
        """
        初始化默认配置文件。

        将默认配置写入文件，API密钥加密存储。
        """
        config = {}
        for key, value in DEFAULT_CONFIG.items():
            if key == "api_key" and value:
                config[key] = _encrypt_value(str(value))
            else:
                config[key] = value

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            try:
                os.chmod(self.config_file, 0o600)
            except OSError:
                pass
        except IOError as e:
            logger.error(f"初始化默认配置失败: {e}")

    def update_config(self, **kwargs) -> Dict[str, Any]:
        """
        更新配置。

        合并传入的配置项到现有配置中，API密钥加密后存储。

        Args:
            **kwargs: 需要更新的配置键值对

        Returns:
            Dict[str, Any]: 更新后的配置（含解密的api_key）

        Raises:
            ValueError: 配置值验证失败时
        """
        current = self.get_config(decrypt=False)

        if "provider" in kwargs:
            provider = kwargs["provider"]
            if provider not in PROVIDERS:
                raise ValueError(f"不支持的提供商: {provider}，支持: {list(PROVIDERS.keys())}")

        if "temperature" in kwargs:
            temp = kwargs["temperature"]
            if not (0 <= temp <= 2):
                raise ValueError("temperature必须在0-2之间")

        if "max_tokens" in kwargs:
            mt = kwargs["max_tokens"]
            if not (1 <= mt <= 32768):
                raise ValueError("max_tokens必须在1-32768之间")

        if "timeout" in kwargs:
            t = kwargs["timeout"]
            if not (5 <= t <= 120):
                raise ValueError("timeout必须在5-120秒之间")

        for key, value in kwargs.items():
            if key in DEFAULT_CONFIG:
                if key == "api_key" and value:
                    current[key] = _encrypt_value(str(value))
                else:
                    current[key] = value

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)

        try:
            os.chmod(self.config_file, 0o600)
        except OSError:
            pass

        return self.get_config(decrypt=True)

    def is_configured(self) -> bool:
        """
        检查是否已配置有效的API信息。

        Returns:
            bool: 是否已配置api_key和provider
        """
        config = self.get_config(decrypt=True)
        return bool(config.get("api_key") and config.get("provider"))

    def get_resolved_config(self) -> Dict[str, Any]:
        """
        获取解析后的完整配置（填充默认值）。

        根据provider自动填充默认的base_url和model。

        Returns:
            Dict[str, Any]: 解析后的配置字典
        """
        config = self.get_config(decrypt=True)
        provider = config.get("provider", "openai")
        provider_info = PROVIDERS.get(provider, PROVIDERS["openai"])

        if not config.get("base_url"):
            config["base_url"] = provider_info["default_base_url"]

        if not config.get("model"):
            config["model"] = provider_info["default_model"]

        return config

    def get_providers(self) -> Dict[str, Any]:
        """
        获取所有支持的提供商信息。

        Returns:
            Dict[str, Any]: 提供商信息字典
        """
        return PROVIDERS
