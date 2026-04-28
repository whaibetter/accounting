import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.llm_config import LlmConfigManager
from app.llm_service import LlmService
from app.dependencies import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"], dependencies=[Depends(require_auth)])


class LlmConfigUpdate(BaseModel):
    provider: Optional[str] = Field(None, description="API提供商")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=32768, description="最大token数")
    timeout: Optional[int] = Field(None, ge=5, le=120, description="超时时间(秒)")


class ParseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="自然语言记账描述")


class ParseAndImportRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="自然语言记账描述")
    default_account: Optional[str] = Field(None, description="默认账户名称")


@router.get("/config", summary="获取LLM配置")
def get_config():
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


@router.get("/config/edit", summary="获取LLM配置(编辑用)")
def get_config_for_edit():
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
    config["has_api_key"] = bool(manager.get_config(decrypt=False).get("api_key"))
    return {"code": 200, "message": "success", "data": config}


@router.put("/config", summary="更新LLM配置")
def update_config(req: LlmConfigUpdate):
    manager = LlmConfigManager()
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的配置")

    if "api_key" not in update_data or not update_data.get("api_key"):
        current = manager.get_config(decrypt=False)
        if current.get("api_key"):
            update_data.pop("api_key", None)

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
    manager = LlmConfigManager()
    providers = manager.get_providers()
    return {"code": 200, "message": "success", "data": providers}


@router.post("/test", summary="测试API连接")
async def test_connection():
    service = LlmService()
    result = await service.test_connection()
    return {"code": 200, "message": "测试完成", "data": result}


@router.post("/parse", summary="解析自然语言为记账数据")
async def parse_text(req: ParseRequest):
    service = LlmService()
    result = await service.parse_text(req.text)

    if not result.get("success"):
        return {"code": 400, "message": result.get("error", "解析失败"), "data": result}

    return {"code": 200, "message": "解析成功", "data": result}


@router.post("/parse-import", summary="解析并导入账单")
async def parse_and_import(req: ParseAndImportRequest, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    service = LlmService()
    parse_result = await service.parse_text(req.text)

    if not parse_result.get("success"):
        return {"code": 400, "message": parse_result.get("error", "解析失败"),
                "data": {"parse_result": parse_result, "import_result": None}}

    bills = parse_result.get("bills", [])
    if not bills:
        return {"code": 400, "message": "未能解析出有效的记账数据",
                "data": {"parse_result": parse_result, "import_result": None}}

    accounts = crud.get_accounts(db, user_id)
    account_map = {acc.name: acc.id for acc in accounts}

    if not account_map:
        return {"code": 400, "message": "请先创建账户后再使用AI记账",
                "data": {"parse_result": parse_result, "import_result": None}}

    default_account_name = req.default_account
    if not default_account_name and accounts:
        default_acc = next((a for a in accounts if a.is_default == 1), accounts[0])
        default_account_name = default_acc.name

    import_bills = []
    for bill in bills:
        account_name = bill.get("account") or default_account_name
        import_bills.append({
            "account": account_name,
            "category": bill.get("category", "其他"),
            "type": bill.get("type", 1),
            "amount": bill.get("amount", 0),
            "date": bill.get("date"),
            "time": bill.get("time"),
            "remark": bill.get("remark", ""),
        })

    try:
        import_result = crud.import_bills_batch(db, user_id, import_bills, account_map)
    except Exception as e:
        logger.error(f"导入账单失败: {e}", exc_info=True)
        return {"code": 500, "message": f"导入失败: {str(e)}",
                "data": {"parse_result": parse_result, "import_result": None}}

    return {
        "code": 200,
        "message": f"成功导入 {import_result.get('success', 0)} 条账单",
        "data": {"parse_result": parse_result, "import_result": import_result},
    }
