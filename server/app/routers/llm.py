import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.llm_config import LlmConfigManager, PROVIDERS
from app.llm_service import LlmService, _mask_api_key
from app.dependencies import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"], dependencies=[Depends(require_auth)])

stream_router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"])


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


@stream_router.get("/test/stream", summary="流式测试API连接(实时进度)")
async def test_connection_stream(token: Optional[str] = None):
    from app.auth import decode_token
    if token:
        try:
            payload = decode_token(token)
            if not payload or not payload.get("user_id"):
                return StreamingResponse(
                    iter([f"data: {json.dumps({'phase': 'error', 'message': '认证失败'}, ensure_ascii=False)}\n\n"]),
                    media_type="text/event-stream",
                )
        except Exception:
            return StreamingResponse(
                iter([f"data: {json.dumps({'phase': 'error', 'message': '认证失败'}, ensure_ascii=False)}\n\n"]),
                media_type="text/event-stream",
            )

    async def event_generator():
        manager = LlmConfigManager()
        if not manager.is_configured():
            yield f"data: {json.dumps({'phase': 'error', 'message': 'API未配置，请先设置API密钥和提供商'}, ensure_ascii=False)}\n\n"
            return

        config = manager.get_resolved_config()
        provider = config.get("provider", "openai")
        provider_info = PROVIDERS.get(provider, {})
        protocol = provider_info.get("protocol", "openai")
        provider_name = provider_info.get("name", provider)

        base_url = config.get("base_url", "").rstrip("/")
        if protocol == "anthropic":
            url = f"{base_url}/v1/messages"
        else:
            url = f"{base_url}/chat/completions"

        safe_headers = {}
        if protocol == "anthropic":
            safe_headers = {
                "x-api-key": _mask_api_key(config.get("api_key", "")),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
        else:
            safe_headers = {
                "Authorization": f"Bearer {_mask_api_key(config.get('api_key', ''))}",
                "Content-Type": "application/json",
            }

        payload = {}
        if protocol == "anthropic":
            payload = {
                "model": config.get("model", "claude-sonnet-4-20250514"),
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
            }
        else:
            payload = {
                "model": config.get("model", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
            }

        request_start_time = time.time()
        request_start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(request_start_time))

        yield f"data: {json.dumps({'phase': 'init', 'message': f'准备测试连接 - {provider_name}', 'provider': provider, 'protocol': protocol}, ensure_ascii=False)}\n\n"
        await asyncio_sleep(0.1)

        yield f"data: {json.dumps({'phase': 'request_prepared', 'message': '请求信息已构建', 'request': {'url': url, 'method': 'POST', 'headers': safe_headers, 'body': payload}, 'timing': {'request_start': request_start_dt, 'request_start_ts': request_start_time}}, ensure_ascii=False)}\n\n"
        await asyncio_sleep(0.1)

        yield f"data: {json.dumps({'phase': 'connecting', 'message': f'正在连接 {base_url} ...'}, ensure_ascii=False)}\n\n"

        import httpx
        timeout = float(config.get("timeout", 30))

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                connect_start = time.time()
                resp = await client.post(url, json=payload, headers={
                    k: (config.get("api_key", "") if "key" in k.lower() or "auth" in k.lower() else v)
                    for k, v in {
                        **({"x-api-key": config.get("api_key", ""), "anthropic-version": "2023-06-01"} if protocol == "anthropic" else {"Authorization": f"Bearer {config.get('api_key', '')}"}),
                        "Content-Type": "application/json",
                    }.items()
                })
                response_start_time = time.time()
                response_start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response_start_time))
                connect_elapsed = (response_start_time - connect_start) * 1000

                yield f"data: {json.dumps({'phase': 'response_received', 'message': f'服务器已响应 (HTTP {resp.status_code})', 'timing': {'response_start': response_start_dt, 'response_start_ts': response_start_time, 'connect_elapsed_ms': round(connect_elapsed)}}, ensure_ascii=False)}\n\n"
                await asyncio_sleep(0.1)

                response_complete_time = time.time()
                response_complete_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response_complete_time))
                total_elapsed = (response_complete_time - request_start_time) * 1000

                response_info = {
                    "status_code": resp.status_code,
                    "headers": dict(resp.headers),
                    "body": resp.text[:2000],
                    "elapsed_ms": round(total_elapsed),
                }

                success = resp.status_code == 200
                result_message = ""
                if success:
                    data = resp.json()
                    model = data.get("model", config.get("model", ""))
                    result_message = f"连接成功，模型: {model}"
                elif resp.status_code == 401:
                    result_message = "API密钥无效"
                elif resp.status_code == 429:
                    result_message = "API调用频率超限，请稍后重试"
                else:
                    result_message = f"API返回错误 (HTTP {resp.status_code}): {resp.text[:200]}"

                yield f"data: {json.dumps({'phase': 'completed', 'message': result_message, 'success': success, 'response': response_info, 'timing': {'response_complete': response_complete_dt, 'response_complete_ts': response_complete_time, 'total_elapsed_ms': round(total_elapsed), 'connect_elapsed_ms': round(connect_elapsed), 'transfer_elapsed_ms': round((response_complete_time - response_start_time) * 1000)}}, ensure_ascii=False)}\n\n"

        except httpx.ConnectError as e:
            error_time = time.time()
            error_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(error_time))
            total_elapsed = (error_time - request_start_time) * 1000
            yield f"data: {json.dumps({'phase': 'error', 'message': f'无法连接到API服务器 {base_url}', 'success': False, 'response': {'error': str(e), 'error_type': 'ConnectError'}, 'timing': {'error_time': error_dt, 'total_elapsed_ms': round(total_elapsed)}}, ensure_ascii=False)}\n\n"
        except httpx.TimeoutException as e:
            error_time = time.time()
            error_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(error_time))
            total_elapsed = (error_time - request_start_time) * 1000
            yield f"data: {json.dumps({'phase': 'error', 'message': '连接超时，请检查网络或增加超时时间', 'success': False, 'response': {'error': str(e), 'error_type': 'TimeoutException'}, 'timing': {'error_time': error_dt, 'total_elapsed_ms': round(total_elapsed)}}, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_time = time.time()
            error_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(error_time))
            total_elapsed = (error_time - request_start_time) * 1000
            yield f"data: {json.dumps({'phase': 'error', 'message': f'连接测试失败: {str(e)}', 'success': False, 'response': {'error': str(e), 'error_type': type(e).__name__}, 'timing': {'error_time': error_dt, 'total_elapsed_ms': round(total_elapsed)}}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def asyncio_sleep(seconds):
    import asyncio
    await asyncio.sleep(seconds)


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
