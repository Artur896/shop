"""MCP-style tool registry the AI Integration Layer exposes to external assistants.

Every tool here does exactly two things beyond the underlying service call:
1. Checks the calling AIPrincipal's token carries the scope the tool needs.
2. Writes an audit log entry recording who (which provider, which user) did what.

None of this contains provider-specific logic — ChatGPT, Claude, and Gemini all call
the same tools through the same scope checks. Adding a new provider never touches
this file or lists_service/items_service; see app/ai/oauth for provider registration.
"""

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Awaitable, Callable

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AIPrincipal
from app.models.enums import ActorType
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.schemas.list import ListCreate
from app.services import items_service, lists_service
from app.services.audit_service import record as record_audit

ToolHandler = Callable[[AsyncSession, AIPrincipal, dict[str, Any], str], Awaitable[Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    required_scopes: list[str]
    handler: ToolHandler


def _require_scopes(principal: AIPrincipal, scopes: list[str]) -> None:
    for scope in scopes:
        principal.require_scope(scope)


async def _audit(
    db: AsyncSession,
    principal: AIPrincipal,
    action: str,
    resource_type: str,
    resource_id: str | None,
    operation_id: str,
    metadata: dict | None = None,
) -> None:
    await record_audit(
        db,
        user_id=principal.user.id,
        actor_type=ActorType.AI,
        actor_id=principal.integration.provider.value,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_id=operation_id,
        metadata=metadata,
    )


async def _get_lists(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["lists:read"])
    name_filter = args.get("name")
    if name_filter:
        matches = await lists_service.find_lists_by_name(db, principal.user.id, name_filter)
        summaries = [await lists_service.get_list_detail(db, m.id, principal.user.id) for m in matches]
        await _audit(db, principal, "get_lists", "list", None, op_id, {"name_filter": name_filter})
        return {
            "lists": [s.model_dump(mode="json") for s in summaries],
            "ambiguous": len(summaries) > 1,
        }

    mine, shared = await lists_service.list_my_lists(db, principal.user.id)
    await _audit(db, principal, "get_lists", "list", None, op_id)
    return {
        "mine": [s.model_dump(mode="json") for s in mine],
        "shared": [s.model_dump(mode="json") for s in shared],
    }


async def _get_list(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["lists:read"])
    list_id = uuid.UUID(args["list_id"])
    summary = await lists_service.get_list_detail(db, list_id, principal.user.id)
    await _audit(db, principal, "get_list", "list", str(list_id), op_id)
    return summary.model_dump(mode="json")


async def _create_list(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["lists:create"])
    data = ListCreate(
        name=args["name"], description=args.get("description"), icon=args.get("icon")
    )
    shopping_list = await lists_service.create_list(db, principal.user.id, data)

    items = args.get("items") or []
    for raw_item in items:
        item_data = ItemCreate(
            name=raw_item["name"],
            quantity=Decimal(str(raw_item.get("quantity", 1))),
            unit=raw_item.get("unit"),
            category=raw_item.get("category", "otros"),
            notes=raw_item.get("notes"),
        )
        await items_service.add_item(db, shopping_list.id, principal.user.id, item_data)

    summary = await lists_service.get_list_detail(db, shopping_list.id, principal.user.id)
    await _audit(
        db, principal, "create_list", "list", str(shopping_list.id), op_id,
        {"name": data.name, "item_count": len(items)},
    )
    return summary.model_dump(mode="json")


async def _add_item(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["items:create"])
    list_id = uuid.UUID(args["list_id"])
    data = ItemCreate(
        name=args["name"],
        quantity=Decimal(str(args.get("quantity", 1))),
        unit=args.get("unit"),
        category=args.get("category", "otros"),
        notes=args.get("notes"),
        estimated_price=Decimal(str(args["estimated_price"])) if args.get("estimated_price") else None,
    )
    item = await items_service.add_item(db, list_id, principal.user.id, data)
    await _audit(db, principal, "add_item", "item", str(item.id), op_id, {"name": data.name, "list_id": str(list_id)})
    return ItemOut.model_validate(item).model_dump(mode="json")


async def _update_item(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["items:update"])
    item_id = uuid.UUID(args["item_id"])
    data = ItemUpdate(
        name=args.get("name"),
        quantity=Decimal(str(args["quantity"])) if args.get("quantity") is not None else None,
        unit=args.get("unit"),
        category=args.get("category"),
        notes=args.get("notes"),
        estimated_price=Decimal(str(args["estimated_price"])) if args.get("estimated_price") else None,
    )
    item = await items_service.update_item(db, item_id, principal.user.id, data)
    await _audit(db, principal, "update_item", "item", str(item_id), op_id)
    return ItemOut.model_validate(item).model_dump(mode="json")


async def _delete_item(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["items:delete"])
    item_id = uuid.UUID(args["item_id"])
    await items_service.delete_item(db, item_id, principal.user.id)
    await _audit(db, principal, "delete_item", "item", str(item_id), op_id)
    return {"deleted": True, "item_id": str(item_id)}


async def _complete_item(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["items:update"])
    item_id = uuid.UUID(args["item_id"])
    item = await items_service.update_item(db, item_id, principal.user.id, ItemUpdate(is_completed=True))
    await _audit(db, principal, "complete_item", "item", str(item_id), op_id)
    return ItemOut.model_validate(item).model_dump(mode="json")


async def _uncomplete_item(db: AsyncSession, principal: AIPrincipal, args: dict, op_id: str) -> Any:
    _require_scopes(principal, ["items:update"])
    item_id = uuid.UUID(args["item_id"])
    item = await items_service.update_item(db, item_id, principal.user.id, ItemUpdate(is_completed=False))
    await _audit(db, principal, "uncomplete_item", "item", str(item_id), op_id)
    return ItemOut.model_validate(item).model_dump(mode="json")


TOOLS: dict[str, ToolDefinition] = {
    t.name: t
    for t in [
        ToolDefinition(
            name="shopping.get_lists",
            description=(
                "List the user's shopping lists. Pass `name` to search by exact name "
                "(use this before modifying a list found by name, to detect duplicates "
                "like two lists both called 'Casa' instead of guessing which one to use)."
            ),
            input_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
            required_scopes=["lists:read"],
            handler=_get_lists,
        ),
        ToolDefinition(
            name="shopping.get_list",
            description="Get one shopping list by id, with its item counts and progress.",
            input_schema={
                "type": "object",
                "properties": {"list_id": {"type": "string", "format": "uuid"}},
                "required": ["list_id"],
            },
            required_scopes=["lists:read"],
            handler=_get_list,
        ),
        ToolDefinition(
            name="shopping.create_list",
            description=(
                "Create a new shopping list for the user, optionally pre-populated with "
                "items. Use this for requests like 'crea una lista para una carne asada "
                "para 10 personas' — infer a sensible item list yourself and pass it."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "icon": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit": {"type": "string"},
                                "category": {"type": "string"},
                                "notes": {"type": "string"},
                            },
                            "required": ["name"],
                        },
                    },
                },
                "required": ["name"],
            },
            required_scopes=["lists:create"],
            handler=_create_list,
        ),
        ToolDefinition(
            name="shopping.add_item",
            description="Add one product to an existing shopping list.",
            input_schema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "category": {"type": "string"},
                    "notes": {"type": "string"},
                    "estimated_price": {"type": "number"},
                },
                "required": ["list_id", "name"],
            },
            required_scopes=["items:create"],
            handler=_add_item,
        ),
        ToolDefinition(
            name="shopping.update_item",
            description="Update fields on an existing product (e.g. change its quantity).",
            input_schema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "category": {"type": "string"},
                    "notes": {"type": "string"},
                    "estimated_price": {"type": "number"},
                },
                "required": ["item_id"],
            },
            required_scopes=["items:update"],
            handler=_update_item,
        ),
        ToolDefinition(
            name="shopping.delete_item",
            description=(
                "Permanently remove a product from a list. Destructive — only usable "
                "if the user has granted the items:delete scope to this integration."
            ),
            input_schema={
                "type": "object",
                "properties": {"item_id": {"type": "string", "format": "uuid"}},
                "required": ["item_id"],
            },
            required_scopes=["items:delete"],
            handler=_delete_item,
        ),
        ToolDefinition(
            name="shopping.complete_item",
            description="Mark a product as purchased/completed.",
            input_schema={
                "type": "object",
                "properties": {"item_id": {"type": "string", "format": "uuid"}},
                "required": ["item_id"],
            },
            required_scopes=["items:update"],
            handler=_complete_item,
        ),
        ToolDefinition(
            name="shopping.uncomplete_item",
            description="Mark a previously-completed product as not purchased.",
            input_schema={
                "type": "object",
                "properties": {"item_id": {"type": "string", "format": "uuid"}},
                "required": ["item_id"],
            },
            required_scopes=["items:update"],
            handler=_uncomplete_item,
        ),
    ]
}


async def invoke_tool(
    db: AsyncSession, principal: AIPrincipal, tool_name: str, arguments: dict, operation_id: str
) -> Any:
    tool = TOOLS.get(tool_name)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown tool: {tool_name}")
    try:
        return await tool.handler(db, principal, arguments or {}, operation_id)
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid arguments: {exc}"
        ) from exc
