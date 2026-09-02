"""The full set of granular permissions an AI integration can be given.

Nothing outside this module should hardcode a scope string — the /profile "AI
permissions" toggle UI, the token-issuance endpoint, and every AI tool's
`required_scopes` all read from here so they can never drift apart.
"""

ALL_SCOPES: list[str] = [
    "lists:read",
    "lists:create",
    "lists:update",
    "lists:delete",
    "items:read",
    "items:create",
    "items:update",
    "items:delete",
    "members:read",
    "members:invite",
]

# What a newly connected integration gets unless the user changes it. Deliberately
# excludes every destructive scope (section 31: deletion needs an explicit opt-in).
DEFAULT_SCOPES: list[str] = [
    "lists:read",
    "lists:create",
    "items:read",
    "items:create",
    "items:update",
]

DESTRUCTIVE_SCOPES: set[str] = {"lists:delete", "items:delete"}

SCOPE_DESCRIPTIONS: dict[str, str] = {
    "lists:read": "Ver mis listas",
    "lists:create": "Crear listas",
    "lists:update": "Modificar listas",
    "lists:delete": "Eliminar listas",
    "items:read": "Ver productos",
    "items:create": "Agregar productos",
    "items:update": "Modificar productos",
    "items:delete": "Eliminar productos",
    "members:read": "Ver miembros",
    "members:invite": "Compartir listas con otros usuarios",
}


def sanitize_scopes(requested: list[str] | None) -> list[str]:
    if requested is None:
        return list(DEFAULT_SCOPES)
    return [s for s in dict.fromkeys(requested) if s in ALL_SCOPES]
