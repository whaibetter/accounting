import json
import logging
import time
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.llm_config import LlmConfigManager, PROVIDERS, _mask_key
from app.llm_service import LlmService, _mask_api_key
from app.dependencies import require_auth
from app.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"], dependencies=[Depends(require_auth)])

stream_router = APIRouter(prefix="/api/v1/llm", tags=["AI智能记账"])


class LlmConfigUpdate(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=32768)
    timeout: Optional[int] = Field(None, ge=5, le=120)
    protocol: Optional[str] = None


class ProviderConfigSave(BaseModel):
    name: str
    provider: Optional[str] = "custom"
    protocol: Optional[str] = "openai"
    api_key: Optional[str] = None
    base_url: Optional[str] = ""
    model: Optional[str] = ""
    temperature: Optional[float] = 0.3
    max_tokens: Optional[int] = 1024
    timeout: Optional[int] = 60


class ProviderConfigLoad(BaseModel):
    name: str


class ProviderConfigDelete(BaseModel):
    name: str


@router.get("/config", summary="获取LLM配置")
def get_config():
    manager = LlmConfigManager()
    config = manager.get_config(decrypt=True)

    if config.get("api_key"):
        key = config["api_key"]
        config["api_key_masked"] = _mask_key(key)
        config["api_key"] = ""

    config["is_configured"] = manager.is_configured()
    return {"code": 200, "message": "success", "data": config}


@router.get("/config/edit", summary="获取LLM配置(编辑用)")
def get_config_for_edit():
    manager = LlmConfigManager()
    config = manager.get_config(decrypt=True)

    if config.get("api_key"):
        key = config["api_key"]
        config["api_key_masked"] = _mask_key(key)
        config["has_api_key"] = True
        config["api_key"] = ""
    else:
        config["has_api_key"] = False

    config["is_configured"] = manager.is_configured()
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
        config["api_key_masked"] = _mask_key(key)
        config["api_key"] = ""

    config["is_configured"] = manager.is_configured()
    return {"code": 200, "message": "配置更新成功", "data": config}


@router.get("/providers", summary="获取支持的提供商列表")
def get_providers():
    return {"code": 200, "message": "success", "data": PROVIDERS}


@router.get("/providers/saved", summary="获取已保存的提供商配置列表")
def get_saved_providers():
    manager = LlmConfigManager()
    configs = manager.get_saved_provider_configs()
    return {"code": 200, "message": "success", "data": configs}


@router.post("/providers/save", summary="保存提供商配置")
def save_provider_config(req: ProviderConfigSave):
    manager = LlmConfigManager()
    config_data = req.model_dump()
    result = manager.save_provider_config(req.name, config_data)
    return {"code": 200, "message": "提供商配置保存成功", "data": result}


@router.post("/providers/load", summary="加载提供商配置")
def load_provider_config(req: ProviderConfigLoad):
    manager = LlmConfigManager()
    config = manager.load_provider_config(req.name)
    if not config:
        raise HTTPException(status_code=404, detail=f"未找到提供商配置: {req.name}")
    return {"code": 200, "message": "success", "data": config}


@router.post("/providers/delete", summary="删除提供商配置")
def delete_provider_config(req: ProviderConfigDelete):
    manager = LlmConfigManager()
    success = manager.delete_provider_config(req.name)
    if not success:
        raise HTTPException(status_code=404, detail=f"未找到提供商配置: {req.name}")
    return {"code": 200, "message": "删除成功"}


@router.post("/test", summary="测试API连接")
async def test_connection():
    service = LlmService()
    result = await service.test_connection()
    return {"code": 200, "message": "测试完成", "data": result}


@stream_router.get("/test/stream", summary="流式测试API连接(实时进度)")
async def test_connection_stream(token: Optional[str] = None):
    if token:
        user_id = verify_token(token)
        if not user_id:
            return StreamingResponse(
                iter([f"data: {json.dumps({'phase': 'error', 'message': '认证失败，请重新登录'}, ensure_ascii=False)}\n\n"]),
                media_type="text/event-stream",
            )
    else:
        return StreamingResponse(
            iter([f"data: {json.dumps({'phase': 'error', 'message': '缺少认证令牌'}, ensure_ascii=False)}\n\n"]),
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
        await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'phase': 'request_prepared', 'message': '请求信息已构建', 'request': {'url': url, 'method': 'POST', 'headers': safe_headers, 'body': payload}, 'timing': {'request_start': request_start_dt, 'request_start_ts': request_start_time}}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'phase': 'connecting', 'message': f'正在连接 {base_url} ...'}, ensure_ascii=False)}\n\n"

        import httpx
        timeout_val = float(config.get("timeout", 30))

        real_headers = {}
        if protocol == "anthropic":
            real_headers = {
                "x-api-key": config.get("api_key", ""),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
        else:
            real_headers = {
                "Authorization": f"Bearer {config.get('api_key', '')}",
                "Content-Type": "application/json",
            }

        try:
            async with httpx.AsyncClient(timeout=timeout_val, proxy=None) as client:
                connect_start = time.time()
                resp = await client.post(url, json=payload, headers=real_headers)
                response_start_time = time.time()
                response_start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response_start_time))
                connect_elapsed = (response_start_time - connect_start) * 1000

                yield f"data: {json.dumps({'phase': 'response_received', 'message': f'服务器已响应 (HTTP {resp.status_code})', 'timing': {'response_start': response_start_dt, 'response_start_ts': response_start_time, 'connect_elapsed_ms': round(connect_elapsed)}}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)

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


@router.post("/parse", summary="解析自然语言为记账数据")
async def parse_text(req: dict):
    text = req.get("text", "")
    service = LlmService()
    result = await service.parse_text(text)
    return {"code": 200, "message": "解析完成", "data": result}


@router.post("/parse-import", summary="解析并导入记账数据")
async def parse_and_import(req: dict, db: Session = Depends(get_db), user_id: int = Depends(require_auth)):
    text = req.get("text", "")
    service = LlmService()
    parse_result = await service.parse_text(text)

    import_result = {"success": 0, "errors": []}

    if parse_result.get("success") and parse_result.get("bills"):
        for bill_data in parse_result["bills"]:
            try:
                category_name = bill_data.get("category", "其他")
                category = crud.get_or_create_category(
                    db,
                    name=category_name,
                    type=bill_data.get("type", 1),
                    user_id=user_id,
                )

                bill = crud.create_bill(
                    db,
                    user_id=user_id,
                    type=bill_data.get("type", 1),
                    amount=bill_data.get("amount", 0),
                    category_id=category.id,
                    date=bill_data.get("date"),
                    time=bill_data.get("time"),
                    remark=bill_data.get("remark", ""),
                )
                if bill:
                    import_result["success"] += 1
                else:
                    import_result["errors"].append(f"创建账单失败: {bill_data}")
            except Exception as e:
                import_result["errors"].append(f"导入失败: {str(e)}")
    else:
        import_result["errors"].append(parse_result.get("error", "解析失败"))

    return {
        "code": 200,
        "message": "操作完成",
        "data": {
            "parse_result": parse_result,
            "import_result": import_result,
        },
    }
