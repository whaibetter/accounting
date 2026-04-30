import json
import os
import hashlib
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_FILE = DATA_DIR / "llm_config.json"
PROVIDERS_FILE = DATA_DIR / "llm_providers.json"

PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "protocol": "openai",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-mini", "o3-mini"],
    },
    "anthropic": {
        "name": "Anthropic",
        "protocol": "anthropic",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-sonnet-4-20250514",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    },
    "openrouter": {
        "name": "OpenRouter",
        "protocol": "openai",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_model": "minimax/minimax-m2.5:free",
        "models": [
            "minimax/minimax-m2.5:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-4-maverick:free",
            "qwen/qwen3-32b:free",
            "tencent/hy3-preview:free",
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "protocol": "openai",
        "default_base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "qwen": {
        "name": "通义千问",
        "protocol": "openai",
        "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
    },
    "siliconflow": {
        "name": "硅基流动",
        "protocol": "openai",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_model": "deepseek-ai/DeepSeek-V3",
        "models": [
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-72B-Instruct",
            "THUDM/GLM-4-9B-0414",
        ],
    },
    "groq": {
        "name": "Groq",
        "protocol": "openai",
        "default_base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    },
    "nvidia": {
        "name": "NVIDIA NIM",
        "protocol": "openai",
        "default_base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "deepseek-ai/deepseek-v4-flash",
        "models": [
            "deepseek-ai/deepseek-v4-flash",
            "deepseek-ai/deepseek-r1",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "qwen/qwen2.5-72b-instruct",
        ],
    },
    "xiaomi": {
        "name": "小米MiMo",
        "protocol": "openai",
        "default_base_url": "https://api.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": [
            "mimo-v2.5-pro",
            "mimo-v2.5",
            "mimo-v2",
        ],
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
    seed = str(DATA_DIR.resolve()) + "accounting_llm_config_salt"
    key_hash = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def _encrypt_value(plain_text: str) -> str:
    if not plain_text:
        return ""
    fernet = Fernet(_get_machine_key())
    return fernet.encrypt(plain_text.encode()).decode()


def _decrypt_value(encrypted: str) -> str:
    if not encrypted:
        return ""
    try:
        fernet = Fernet(_get_machine_key())
        return fernet.decrypt(encrypted.encode()).decode()
    except Exception as e:
        logger.warning(f"解密失败: {e}")
        return ""


class LlmConfigManager:
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or CONFIG_FILE
        DATA_DIR.mkdir(exist_ok=True)
        self._init_default_providers()

    def get_config(self, decrypt: bool = True) -> Dict[str, Any]:
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

    def _init_default_providers(self) -> None:
        if PROVIDERS_FILE.exists():
            return

        default_presets = [
            {
                "name": "OpenRouter",
                "provider": "openrouter",
                "protocol": "openai",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "minimax/minimax-m2.5:free",
                "temperature": 0.3,
                "max_tokens": 1024,
                "timeout": 60,
                "api_key": _encrypt_value(DEFAULT_API_KEY),
            },
            {
                "name": "NVIDIA NIM",
                "provider": "nvidia",
                "protocol": "openai",
                "base_url": "https://integrate.api.nvidia.com/v1",
                "model": "deepseek-ai/deepseek-v4-flash",
                "temperature": 0.6,
                "max_tokens": 16384,
                "timeout": 120,
                "api_key": _encrypt_value("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"),
            },
            {
                "name": "小米MiMo",
                "provider": "xiaomi",
                "protocol": "openai",
                "base_url": "https://api.xiaomimimo.com/v1",
                "model": "mimo-v2.5-pro",
                "temperature": 1.0,
                "max_tokens": 1024,
                "timeout": 60,
                "api_key": _encrypt_value("sk-swl7zp9bvo1yu1n5ojo7f96vleqxgbfa23umfznqiawn1siy"),
            },
        ]

        try:
            with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_presets, f, ensure_ascii=False, indent=2)
            try:
                os.chmod(PROVIDERS_FILE, 0o600)
            except OSError:
                pass
        except IOError as e:
            logger.error(f"初始化默认提供商配置失败: {e}")

    def update_config(self, **kwargs) -> Dict[str, Any]:
        current = self.get_config(decrypt=False)

        if "provider" in kwargs:
            provider = kwargs["provider"]
            if provider not in PROVIDERS and provider != "custom":
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
            if key in DEFAULT_CONFIG or key == "protocol":
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
        config = self.get_config(decrypt=True)
        return bool(config.get("api_key") and config.get("provider"))

    def get_resolved_config(self) -> Dict[str, Any]:
        config = self.get_config(decrypt=True)
        provider = config.get("provider", "openai")
        provider_info = PROVIDERS.get(provider, {})

        if not config.get("base_url"):
            config["base_url"] = provider_info.get("default_base_url", "")

        if not config.get("model"):
            config["model"] = provider_info.get("default_model", "")

        return config

    def get_providers(self) -> Dict[str, Any]:
        return PROVIDERS

    def get_saved_provider_configs(self) -> List[Dict[str, Any]]:
        if not PROVIDERS_FILE.exists():
            return []

        try:
            with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                configs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

        for cfg in configs:
            if cfg.get("api_key"):
                key = _decrypt_value(cfg["api_key"])
                if key:
                    cfg["api_key_masked"] = _mask_key(key)
                cfg.pop("api_key", None)

        return configs

    def save_provider_config(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        configs = []
        if PROVIDERS_FILE.exists():
            try:
                with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                    configs = json.load(f)
            except (json.JSONDecodeError, IOError):
                configs = []

        existing = next((c for c in configs if c.get("name") == name), None)

        save_data = {
            "name": name,
            "provider": config.get("provider", "custom"),
            "protocol": config.get("protocol", "openai"),
            "base_url": config.get("base_url", ""),
            "model": config.get("model", ""),
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 1024),
            "timeout": config.get("timeout", 60),
        }

        if config.get("api_key"):
            save_data["api_key"] = _encrypt_value(config["api_key"])

        if existing:
            if not config.get("api_key") and existing.get("api_key"):
                save_data["api_key"] = existing["api_key"]
            configs = [c for c in configs if c.get("name") != name]
            configs.append(save_data)
        else:
            configs.append(save_data)

        with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)

        try:
            os.chmod(PROVIDERS_FILE, 0o600)
        except OSError:
            pass

        result = {**save_data}
        if result.get("api_key"):
            key = _decrypt_value(result["api_key"])
            result["api_key_masked"] = _mask_key(key) if key else "****"
            result.pop("api_key", None)

        return result

    def load_provider_config(self, name: str) -> Optional[Dict[str, Any]]:
        if not PROVIDERS_FILE.exists():
            return None

        try:
            with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                configs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        cfg = next((c for c in configs if c.get("name") == name), None)
        if not cfg:
            return None

        result = {**cfg}
        if result.get("api_key"):
            key = _decrypt_value(result["api_key"])
            result["api_key"] = key
            result["api_key_masked"] = _mask_key(key) if key else "****"
            result["has_api_key"] = bool(key)
        else:
            result["has_api_key"] = False

        return result

    def delete_provider_config(self, name: str) -> bool:
        if not PROVIDERS_FILE.exists():
            return False

        try:
            with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
                configs = json.load(f)
        except (json.JSONDecodeError, IOError):
            return False

        original_len = len(configs)
        configs = [c for c in configs if c.get("name") != name]

        if len(configs) == original_len:
            return False

        with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)

        return True


def _mask_key(key: str) -> str:
    if not key:
        return "(空)"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"
