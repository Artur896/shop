"""The AI-facing surface of the application: REST endpoints (section 37) and an
MCP-style tool catalog (section 26), both authenticated with a scoped AI token
(never the user's own JWT) and enforcing exactly the same authorization rules as
/lists and /items — see app/ai/tools/definitions.py for where that reuse happens.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AIPrincipal, get_ai_principal
from app.db.session import get_db
from app.ai.tools.definitions import TOOLS, invoke_tool

router = APIRouter(prefix="/ai", tags=["ai"])


def _operation_id() -> str:
    return uuid.uuid4().hex


class ToolDescriptor(BaseModel):
    name: str
    description: str
    input_schema: dict
    required_scopes: list[str]


class ToolInvokeRequest(BaseModel):
    tool: str
    arguments: dict = {}


class ToolInvokeResponse(BaseModel):
    operation_id: str
    result: dict | list | None = None


@router.get("/mcp/tools", response_model=list[ToolDescriptor])
async def list_tools(principal: AIPrincipal = Depends(get_ai_principal)) -> list[ToolDescriptor]:
    return [
        ToolDescriptor(
            name=t.name,
            description=t.description,
            input_schema=t.input_schema,
            required_scopes=t.required_scopes,
        )
        for t in TOOLS.values()
        if any(principal.has_scope(s) for s in t.required_scopes) or not t.required_scopes
    ]


@router.post("/mcp/invoke", response_model=ToolInvokeResponse)
async def invoke(
    payload: ToolInvokeRequest,
    principal: AIPrincipal = Depends(get_ai_principal),
    db: AsyncSession = Depends(get_db),
) -> ToolInvokeResponse:
    op_id = _operation_id()
    try:
        result = await invoke_tool(db, principal, payload.tool, payload.arguments, op_id)
    except HTTPException:
        await db.commit()  # persist the audit trail even for a denied/failed call
        raise
    await db.commit()
    return ToolInvokeResponse(operation_id=op_id, result=result)


@router.get("/lists")
async def ai_get_lists(
    name: str | None = None,
    principal: AIPrincipal = Depends(get_ai_principal),
    db: AsyncSession = Depends(get_db),
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.get_lists", {"name": name} if name else {}, op_id)
    await db.commit()
    return result


@router.get("/lists/{list_id}")
async def ai_get_list(
    list_id: uuid.UUID, principal: AIPrincipal = Depends(get_ai_principal), db: AsyncSession = Depends(get_db)
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.get_list", {"list_id": str(list_id)}, op_id)
    await db.commit()
    return result


class AICreateListBody(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    items: list[dict] | None = None


@router.post("/lists", status_code=status.HTTP_201_CREATED)
async def ai_create_list(
    payload: AICreateListBody,
    principal: AIPrincipal = Depends(get_ai_principal),
    db: AsyncSession = Depends(get_db),
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.create_list", payload.model_dump(), op_id)
    await db.commit()
    return result


@router.post("/lists/{list_id}/items", status_code=status.HTTP_201_CREATED)
async def ai_add_item(
    list_id: uuid.UUID,
    payload: dict,
    principal: AIPrincipal = Depends(get_ai_principal),
    db: AsyncSession = Depends(get_db),
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.add_item", {**payload, "list_id": str(list_id)}, op_id)
    await db.commit()
    return result


@router.patch("/items/{item_id}")
async def ai_update_item(
    item_id: uuid.UUID,
    payload: dict,
    principal: AIPrincipal = Depends(get_ai_principal),
    db: AsyncSession = Depends(get_db),
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.update_item", {**payload, "item_id": str(item_id)}, op_id)
    await db.commit()
    return result


@router.delete("/items/{item_id}")
async def ai_delete_item(
    item_id: uuid.UUID, principal: AIPrincipal = Depends(get_ai_principal), db: AsyncSession = Depends(get_db)
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.delete_item", {"item_id": str(item_id)}, op_id)
    await db.commit()
    return result


@router.post("/items/{item_id}/complete")
async def ai_complete_item(
    item_id: uuid.UUID, principal: AIPrincipal = Depends(get_ai_principal), db: AsyncSession = Depends(get_db)
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.complete_item", {"item_id": str(item_id)}, op_id)
    await db.commit()
    return result


@router.post("/items/{item_id}/uncomplete")
async def ai_uncomplete_item(
    item_id: uuid.UUID, principal: AIPrincipal = Depends(get_ai_principal), db: AsyncSession = Depends(get_db)
):
    op_id = _operation_id()
    result = await invoke_tool(db, principal, "shopping.uncomplete_item", {"item_id": str(item_id)}, op_id)
    await db.commit()
    return result
