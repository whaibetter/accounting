"""
大模型API集成路由模块。

功能描述：
    提供大模型API配置管理和智能记账功能的HTTP接口，包括：
    - 获取/更新API配置
    - 获取支持的提供商列表
    - 测试API连接
    - 自然语言文本解析为记账数据
    - 解析并直接导入账单

接口列表：
    GET  /api/v1/llm/config        获取当前配置
    PUT  /api/v1/llm/config        更新配置
    GET  /api/v1/llm/providers     获取提供商列表
    POST /api/v1/llm/test          测试连接
    POST /api/v1/llm/parse         解析文本
    POST /api/v1/llm/parse-import  解析并导入

认证要求：
    所有接口均需JWT Token认证
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.llm_config import LlmConfigManager
from app.llm_service import LlmService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"])


class LlmConfigUpdate(BaseModel):
    """
    更新LLM配置请求体。

    Attributes:
        provider: API提供商 (openai/anthropic/custom)
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        temperature: 温度参数 (0-2)
        max_tokens: 最大token数 (1-32768)
        timeout: 超时时间 (5-120秒)
    """
    provider: Optional[str] = Field(None, description="API提供商: openai/anthropic/custom")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=32768, description="最大token数")
    timeout: Optional[int] = Field(None, ge=5, le=120, description="超时时间(秒)")


class ParseRequest(BaseModel):
    """
    文本解析请求体。

    Attributes:
        text: 自然语言记账描述文本
    """
    text: str = Field(..., min_length=1, max_length=2000, description="自然语言记账描述")


class ParseAndImportRequest(BaseModel):
    """
    解析并导入请求体。

    Attributes:
        text: 自然语言记账描述文本
        default_account: 默认账户名称（当解析结果中无账户时使用）
    """
    text: str = Field(..., min_length=1, max_length=2000, description="自然语言记账描述")
    default_account: Optional[str] = Field(None, description="默认账户名称")


@router.get("/config", summary="获取LLM配置")
def get_config():
    """
    获取当前大模型API配置。

    返回的api_key会被脱敏处理，仅显示前4位和后4位。

    Returns:
        配置信息字典，api_key已脱敏
    """
    manager = LlmConfigManager()
    config = manager.get_config(decrypt=True)

    if config.get("api_key"):
        key = config["api_key"]
        if len(key) > 8:
            config["api_key_masked"] = key[:4] + "*" * (len(key) - 8) + key[-4:]
        else:
            config["api_key_masked"] = "****"
        config["api_key"] = ""

    config["is_configured"] = manager.is_configured()

    return {"code": 200, "message": "success", "data": config}


@router.put("/config", summary="更新LLM配置")
def update_config(req: LlmConfigUpdate):
    """
    更新大模型API配置。

    仅更新传入的非None字段。API密钥会加密存储。

    Returns:
        更新后的配置信息
    """
    manager = LlmConfigManager()

    update_data = {}
    for key, value in req.model_dump().items():
        if value is not None:
            update_data[key] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的配置")

    try:
        config = manager.update_config(**update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if config.get("api_key"):
        key = config["api_key"]
        if len(key) > 8:
            config["api_key_masked"] = key[:4] + "*" * (len(key) - 8) + key[-4:]
        else:
            config["api_key_masked"] = "****"
        config["api_key"] = ""

    config["is_configured"] = manager.is_configured()

    return {"code": 200, "message": "配置更新成功", "data": config}


@router.get("/providers", summary="获取支持的API提供商")
def get_providers():
    """
    获取所有支持的大模型API提供商信息。

    Returns:
        提供商信息字典，包含名称、默认URL、可用模型列表
    """
    manager = LlmConfigManager()
    providers = manager.get_providers()
    return {"code": 200, "message": "success", "data": providers}


@router.post("/test", summary="测试API连接")
async def test_connection():
    logger.info("[API] 测试API连接请求")
    service = LlmService()
    result = await service.test_connection()
    logger.info(f"[API] 测试结果: success={result.get('success')}, message={result.get('message')}")
    return {"code": 200, "message": "测试完成", "data": result}


@router.post("/parse", summary="解析自然语言为记账数据")
async def parse_text(req: ParseRequest):
    logger.info(f"[API] 解析请求: text='{req.text[:50]}{'...' if len(req.text) > 50 else ''}'")
    service = LlmService()
    result = await service.parse_text(req.text)

    if not result.get("success"):
        logger.warning(f"[API] 解析失败: {result.get('error')}")
        return {
            "code": 400,
            "message": result.get("error", "解析失败"),
            "data": result,
        }

    logger.info(f"[API] 解析成功: {len(result.get('bills', []))} 条账单")
    return {"code": 200, "message": "解析成功", "data": result}


@router.post("/parse-import", summary="解析并导入账单")
async def parse_and_import(req: ParseAndImportRequest, db: Session = Depends(get_db)):
    logger.info(f"[API] 解析并导入请求: text='{req.text[:50]}{'...' if len(req.text) > 50 else ''}', default_account={req.default_account}")

    service = LlmService()
    parse_result = await service.parse_text(req.text)

    if not parse_result.get("success"):
        logger.warning(f"[API] 解析失败: {parse_result.get('error')}")
        return {
            "code": 400,
            "message": parse_result.get("error", "解析失败"),
            "data": {"parse_result": parse_result, "import_result": None},
        }

    bills = parse_result.get("bills", [])
    if not bills:
        logger.warning("[API] 未能解析出有效账单")
        return {
            "code": 400,
            "message": "未能解析出有效的记账数据",
            "data": {"parse_result": parse_result, "import_result": None},
        }

    accounts = crud.get_accounts(db)
    account_map = {acc.name: acc.id for acc in accounts}

    if not account_map:
        logger.warning("[API] 用户没有账户")
        return {
            "code": 400,
            "message": "请先创建账户后再使用AI记账",
            "data": {"parse_result": parse_result, "import_result": None},
        }

    default_account_name = req.default_account
    if not default_account_name and accounts:
        default_acc = next((a for a in accounts if a.is_default == 1), accounts[0])
        default_account_name = default_acc.name

    import_bills = []
    for bill in bills:
        account_name = bill.get("account") or default_account_name

        import_item = {
            "account": account_name,
            "category": bill.get("category", "其他"),
            "type": bill.get("type", 1),
            "amount": bill.get("amount", 0),
            "date": bill.get("date"),
            "time": bill.get("time"),
            "remark": bill.get("remark", ""),
        }
        import_bills.append(import_item)

    logger.info(f"[API] 准备导入 {len(import_bills)} 条账单")

    try:
        import_result = crud.import_bills_batch(db, import_bills, account_map)
        logger.info(f"[API] 导入完成: success={import_result.get('success')}, errors={len(import_result.get('errors', []))}")
    except Exception as e:
        logger.error(f"[API] 导入账单失败: {e}", exc_info=True)
        return {
            "code": 500,
            "message": f"导入失败: {str(e)}",
            "data": {"parse_result": parse_result, "import_result": None},
        }

    return {
        "code": 200,
        "message": f"成功导入 {import_result.get('success', 0)} 条账单",
        "data": {
            "parse_result": parse_result,
            "import_result": import_result,
        },
    }
